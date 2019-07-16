from flask import *
from ruqqus.classes import *
from ruqqus.helpers.wrappers import *
from ruqqus.helpers.base36 import *
from secrets import token_hex
from time import time
import hmac
from os import environ
import re

from ruqqus.mail import *
from ruqqus.__main__ import app

valid_username_regex=re.compile("^\w{5,}$")
valid_password_regex=re.compile("^.{8,}$")

#login form
@app.route("/login", methods=["GET"])
@auth_desired
def login_get(v):
    if v:
        return redirect("/")

    return render_template("login.html", failed=False)

#login post procedure
@app.route("/login", methods=["POST"])
def login_post():

    username=request.form.get("username")

    #step1: identify if username is username or email
    if "@" in username:
        try:
            account = db.query(User).filter_by(email=username).first()
        except IndexError:
            return render_template("login.html", failed=True)

    else:
        try:
            account = db.query(User).filter_by(username=username).first()
        except IndexError:
            return render_template("login.html", failed=True)

    #test password
    if account.verifyPass(request.form.get("password")):

        #set session user id
        session["user_id"]=account.id
        session["session_id"]=token_hex(16)

        return redirect(account.url)

    else:
        return render_template("login.html", failed=True)

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
    
    #Make a unique form key valid for one account creation
    now = int(time())
    token = token_hex(16)
    session["signup_token"]=token
    ip=request.remote_addr
    
    formkey_hashstr = str(now)+token+ip+agent

    
    #formkey is a hash of session token, timestamp, and IP address
    formkey = hmac.new(key=bytes(environ.get("MASTER_KEY"), "utf-16"),
                       msg=bytes(formkey_hashstr, "utf-16")
                       ).hexdigest()
    
    return render_template("sign_up.html", formkey=formkey, now=now)

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
    ip=request.remote_addr
    
    correct_formkey_hashstr = form_timestamp+submitted_token+ip+agent
    
    correct_formkey = hmac.new(key=bytes(environ.get("MASTER_KEY"), "utf-16"),
                               msg=bytes(correct_formkey_hashstr, "utf-16")
                               ).hexdigest()
    
    now=int(time())
    

    #define function that takes an error message and generates a new signup form
    def new_signup(error):
        
        #Reset tokens and return to signup form
        
        token = token_hex(16)
        session["signup_token"]=token
        now=int(time())
        agent=request.headers.get("User-Agent", None)
        ip=request.remote_addr

        new_formkey_hashstr=str(now)+submitted_token+ip+agent
        new_formkey = hmac.new(key=bytes(environ.get("MASTER_KEY"), "utf-16"),
                               msg=bytes(new_formkey_hashstr, "utf-16")
                               ).hexdigest()
        
        return render_template("sign_up.html", formkey=new_formkey, now=now, error=error)

    #check for tokens
    if now-int(form_timestamp)>120:
        print("form expired")
        return new_signup("There was a problem. Please refresh the page and try again.")
    elif now-int(form_timestamp)<5:
        print("slow down!")
        return new_signup("There was a problem. Please refresh the page and try again.")

    if not hmac.compare_digest(correct_formkey, form_formkey):
        print(f"{request.form.get('username')} - mismatched formkeys")
        return new_signup("There was a problem. Please refresh the page and try again.")

    #check for matched passwords
    if not request.form.get("password") == request.form.get("password_confirm"):
        return new_signup("Password and Confirm Password do not match.")

    #check username/pass conditions
    if not re.match(valid_username_regex, request.form.get("username")):
        return new_signup("Invalid username")

    if not re.match(valid_password_regex, request.form.get("password")):
        return new_signup("Password must be 8 characters or longer")

    #Check for existing acocunts

    if (db.query(User).filter(User.username.ilike(request.form.get("username"))).first()
        or db.query(User).filter(User.email.ilike(request.form.get("email"))).first()):
        return new_signup("An account with that username or email already exists.")       
    
    #success
    
    #kill tokens
    session.pop("signup_token")
    
    #make new user
    try:
        new_user=User(username=request.form.get("username"),
                      password=request.form.get("password"),
                      email=request.form.get("email"),
                      created_utc=int(time()),
                      creation_ip=request.remote_addr
                 )

    except Exception as e:
        print(e)
        return new_signup("Please enter a valid email")
    
    db.add(new_user)
    db.commit()

    v=db.query(User).filter_by(username=request.form.get("username")).first()



    #send_mail(to_address=new_user.email, from_address=None,
    #          subject="T_D Account Activation",
    #          plaintext=f"http://tee-dee.herokuapp.com/activate?hash={v.activehash}", html=None)

    session["user_id"]=v.id
    session["session_id"]=token_hex(16)
    
    return redirect(v.url)
    