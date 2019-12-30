from flask import *
import time
import hmac
from os import environ
import re
import random
from urllib.parse import urlencode

from ruqqus.classes import *
from ruqqus.helpers.wrappers import *
from ruqqus.helpers.base36 import *
from ruqqus.helpers.security import *
from ruqqus.mail import send_verification_email
from secrets import token_hex


from ruqqus.mail import *
from ruqqus.__main__ import app, limiter

valid_username_regex=re.compile("^\w{5,25}$")
valid_password_regex=re.compile("^.{8,}$")
#valid_email_regex=re.compile("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

#login form
@app.route("/login", methods=["GET"])
@auth_desired
def login_get(v):


    redir=request.args.get("redirect","/")
    if v:
        return redirect(redir)
    

    return render_template("login.html",
                           failed=False,
                           i=random_image(),
                           redirect=redir)

def check_for_alts(current_id):
    #account history
    past_accs=set(session.get("history", []))
    past_accs.add(current_id)
    session["history"]=list(past_accs)

    #record alts
    for past_id in session["history"]:

        if past_id==current_id:
            continue
        
        check1=db.query(Alt).filter_by(user1=current_id, user2=past_id).first()
        check2=db.query(Alt).filter_by(user1=past_id, user2=current_id).first()

        if not check1 and not check2:

            new_alt=Alt(user1=past_id,
                        user2=current_id)
            db.add(new_alt)
            db.commit()

#login post procedure
@app.route("/login", methods=["POST"])
@limiter.limit("6/minute")
def login_post():
    
    username=request.form.get("username")

    if "@" in username:
        account=db.query(User).filter(User.email.ilike(username)).first()
    else:
        account=db.query(User).filter(User.username.ilike(username)).first()

    if not account:
        time.sleep(random.uniform(0,2))
        return render_template("login.html", failed=True, i=random_image())

    #test password
    if not account.verifyPass(request.form.get("password")):
        time.sleep(random.uniform(0,2))
        return render_template("login.html", failed=True, i=random_image())

    #set session and user id
    session["user_id"]=account.id
    session["session_id"]=token_hex(16)

    check_for_alts(account.id)

    #check self-setting badges
    badge_types = db.query(BadgeDef).filter(BadgeDef.qualification_expr.isnot(None)).all()
    for badge in badge_types:
        if eval(badge.qualification_expr, {}, {'v':account}):
            if not account.has_badge(badge.id):
                new_badge=Badge(user_id=account.id,
                                badge_id=badge.id,
                                created_utc=int(time.time())
                                )
                db.add(new_badge)
                db.commit()
        else:
            bad_badge=account.has_badge(badge.id)
            if bad_badge:
                db.delete(bad_badge)
                db.commit()

    #check for previous page

    redir=request.form.get("redirect", "/")
    if redir:
        return redirect(redir)
    else:
        return redirect(account.url)

@app.route("/me", methods=["GET"])
@auth_required
def me(v):
    return redirect(v.url)


@app.route("/logout", methods=["POST"])
@auth_required
@validate_formkey
def logout(v):

    session.pop("user_id", None)
    session.pop("session_id", None)

    return redirect("/")

#signing up
@app.route("/signup", methods=["GET"])
@auth_desired
def sign_up_get(v):
    if v:
        return redirect("/")
    
    agent=request.headers.get("User-Agent", None)
    if not agent:
        abort(403)

    #check for referral in link
    ref_id=None
    ref = request.args.get("ref",None)
    if ref:
        ref_user = db.query(User).filter(User.username.ilike(ref)).first()

    else:
        ref_user=None

    if ref_user and (ref_user.id in session.get("history", [])):
        return render_template("sign_up_failed_ref.html",
                               i=random_image())
    
    
    #Make a unique form key valid for one account creation
    now = int(time.time())
    token = token_hex(16)
    session["signup_token"]=token
    ip=request.remote_addr
    
    formkey_hashstr = str(now)+token+agent

    
    #formkey is a hash of session token, timestamp, and IP address
    formkey = hmac.new(key=bytes(environ.get("MASTER_KEY"), "utf-16"),
                       msg=bytes(formkey_hashstr, "utf-16")
                       ).hexdigest()

    redir = request.args.get("redirect",None)

    error= request.args.get("error", None)



    return render_template("sign_up.html",
                           formkey=formkey,
                           now=now,
                           i=random_image(),
                           redirect=redir,
                           ref_user=ref_user,
                           error=error
                           )

#signup api
@app.route("/signup", methods=["POST"])
@auth_desired
def sign_up_post(v):
    if v:
        abort(403)
        
    agent=request.headers.get("User-Agent", None)
    if not agent:
        abort(403)
    
    form_timestamp = request.form.get("now", 0)
    form_formkey = request.form.get("formkey","none")
    
    submitted_token=session["signup_token"]
    
    correct_formkey_hashstr = form_timestamp+submitted_token+agent
    
    correct_formkey = hmac.new(key=bytes(environ.get("MASTER_KEY"), "utf-16"),
                               msg=bytes(correct_formkey_hashstr, "utf-16")
                               ).hexdigest()
    
    now=int(time.time())

    username=request.form.get("username")

    #define function that takes an error message and generates a new signup form
    def new_signup(error):

        args={"error":error}
        if request.form.get("referred_by"):
            user=db.query(User).filter_by(id=request.form.get("referred_by")).first()
            if user:
                args["ref"]=user.username
        
        
        return redirect(f"/signup?{urlencode(args)}")

    #check for tokens
##    if now-int(form_timestamp)>120:
##        print(f"signup fail - {username } - form expired")
        
        return new_signup("There was a problem. Please try again.")
    if now-int(form_timestamp)<5:
        print(f"signup fail - {username } - too fast")
        return new_signup("There was a problem. Please try again.")

    if not hmac.compare_digest(correct_formkey, form_formkey):
        print(f"signup fail - {username } - mismatched formkeys")
        return new_signup("There was a problem. Please try again.")

    #check for matched passwords
    if not request.form.get("password") == request.form.get("password_confirm"):
        return new_signup("Passwords did not match. Please try again.")

    #check username/pass conditions
    if not re.match(valid_username_regex, request.form.get("username")):
        print(f"signup fail - {username } - mismatched passwords")
        return new_signup("Invalid username")

    if not re.match(valid_password_regex, request.form.get("password")):
        print(f"signup fail - {username } - invalid password")
        return new_signup("Password must be 8 characters or longer")

    #if not re.match(valid_email_regex, request.form.get("email")):
    #    return new_signup("That's not a valid email.")

    #Check for existing acocunts
    email=request.form.get("email")
    if not email:
        email=None

    if (db.query(User).filter(User.username.ilike(request.form.get("username"))).first()
        or (email and db.query(User).filter(User.email.ilike(email)).first())):
        print(f"signup fail - {username } - email already exists")
        return new_signup("An account with that username or email already exists.")
    
    #success
    
    #kill tokens
    session.pop("signup_token")

    #get referral
    ref_id = int(request.form.get("referred_by", 0))
    ref_id=None if not ref_id else ref_id

    #upgrade user badge
    ref_user=db.query(User).filter_by(id=ref_id).first()
    if not ref_user:
        ref_id=None
        
    
        
    #make new user
    try:
        new_user=User(username=username,
                      password=request.form.get("password"),
                      email=email,
                      created_utc=int(time.time()),
                      creation_ip=request.remote_addr,
                      referred_by=ref_id
                 )

    except Exception as e:
        print(e)
        return new_signup("Please enter a valid email")
    
    db.add(new_user)
    db.commit()

    #give a beta badge
    beta_badge=Badge(user_id=new_user.id,
                        badge_id=1)

    db.add(beta_badge)
    db.commit()

    #upgrade referring user's recruitment badge
    if ref_user:
        if ref_user.referral_count >=100:
            badge=db.query(Badge).filter(Badge.user_id==ref_user.id,
                                         Badge.badge_id.in_([10,11])).first()
            if badge:
                badge.badge_id=12
                db.add(badge)
                db.commit()
        elif ref_user.referral_count >=10:
            badge=db.query(Badge).filter_by(user_id=ref_user.id,
                                            badge_id=10).first()
            if badge:
                badge.badge_id=11
                db.add(badge)
                db.commit()

        else:
            badge=db.query(Badge).filter_by(user_id=ref_user.id,
                                            badge_id=10).first()
            if not badge:
                new_badge=Badge(user_id=ref_user.id,
                                badge_id=10,
                                created_utc=int(time.time())
                                )
                db.add(new_badge)
                db.commit()
                
                                      

    #check alts

    check_for_alts(new_user.id)

    if email:
        send_verification_email(new_user)

    session["user_id"]=new_user.id
    session["session_id"]=token_hex(16)

    redir=request.form.get("redirect", None)
    if redir:
        return redirect(redir)
    else:
        return redirect(new_user.permalink)
    

@app.route("/forgot", methods=["GET"])
def get_forgot():

    return render_template("forgot_password.html",
                           i=random_image()
                           )

@app.route("/forgot", methods=["POST"])
def post_forgot():

    username = request.form.get("username")
    email = request.form.get("email")

    user = db.query(User).filter(User.username.ilike(username), User.email.ilike(email), User.is_activated==True).first()

    if user:
        #generate url
        now=int(time.time())
        token=generate_hash(f"{user.id}+{now}+forgot")
        url=f"https://{app.config['SERVER_NAME']}/reset?id={user.id}&time={now}&token={token}"

        send_mail(to_address=user.email,
                  subject="Ruqqus - Password Reset Request",
                  html=render_template("email/password_reset.html",
                                       action_url=url,
                                       v=user)
                  )

    return render_template("forgot_password.html",
                           msg="If the username and email matches an account, you will be sent a password reset email. You have ten minutes to complete the password reset process.",
                           i=random_image())


@app.route("/reset", methods=["GET"])
def get_reset():


    user_id = request.args.get("id")
    timestamp=int(request.args.get("time"))
    token=request.args.get("token")

    now=int(time.time())

    if now-timestamp > 600:
        return render_template("message.html", title="Password reset link expired", text="That password reset link has expired.")

    if not validate_hash(f"{user_id}+{timestamp}+forgot", token):
        abort(400)
                           
    user=db.query(User).filter_by(id=user_id).first()

    if not user:
        abort(404)

    reset_token=generate_hash(f"{user.id}+{timestamp}+reset")

    return render_template("reset_password.html",
                           v=user,
                           token=reset_token,
                           time=timestamp,
                           i=random_image()
                           )


@app.route("/reset", methods=["POST"])
def post_reset():

    user_id=request.form.get("user_id")
    timestamp=int(request.form.get("time"))
    token=request.form.get("token")

    password=request.form.get("password")
    confirm_password=request.form.get("confirm_password")

    now=int(time.time())

    if now-timestamp>600:
        return render_template("message.html",
                               title="Password reset expired",
                               text="That password reset form has expired.")

    if not validate_hash(f"{user_id}+{timestamp}+reset", token):
        abort(400)

    user=db.query(User).filter_by(id=user_id).first()
    if not user:
        abort(404)

    if not password==confirm_password:
        return render_template("reset_password.html",
                               v=user,
                               token=token,
                               time=timestamp,
                               i=random_image(),
                               error="Passwords didn't match.")

    user.passhash = hash_password(password)
    db.add(user)
    db.commit()

    return render_template("message_success.html",
                           title="Password reset successful!",
                           text="Login normally to access your account.")
