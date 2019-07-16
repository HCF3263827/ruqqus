import praw
from os import environ
from flask import *
from ruqqus.classes import *
from ruqqus.helpers.wrappers import *
from secrets import token_hex
from ruqqus.__main__ import db, app

r=praw.Reddit(client_id=environ.get("reddit_id"),
              client_secret=environ.get("reddit_secret"),
              user_agent="ruqqus username verification by /u/captainmeta4",
              redirect_uri="https://tee-dee.herokuapp.com/api/redditredirect")

@app.route("/api/get_reddit_auth")
@auth_required
def api_get_reddit_auth(v):
    return redirect(r.auth.url(scopes=["identity"],
                               state=session["session_id"],
                               duration="temporary"))

@app.route("/api/redditredirect")
@auth_required
def api_redditredirect(v):

    #check session id
    if not request.args.get("state")==session["session_id"]:
        return render_template("settings.html", v=v, error="Invalid token. Please try again.")

    try:
        r.auth.authorize(request.args.get("code"))
        name = r.user.me().name
    except Exception as e:
        print(e)
        return render_template("settings.html", v=v, error="Unable to check reddit username.")

    #run username verification procedure
    return v.verify_username(name)
    