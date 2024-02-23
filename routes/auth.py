from app import app
from utils.db_conn import connect
from db_config import db_settings
from flask import request, render_template, send_file, make_response, session, redirect

from utils.email_utils import send_email_from_dict

import string
import uuid

@app.route("/auth/login", methods=["GET", "POST"])
def login_page():
    print(request.args.get("referred"))
    redir = request.args.get("referred") if request.args.get("referred") else "/"
    if session.get("loggedin"):
        return redirect(redir, code=302)

    username = ""
    password = ""

    username_error = "~"
    password_error = "~"
    login_error = "~"

    if request.method == "POST":
        if request.form["username"].strip() == "":
            username_error = "Please enter a username"
        else:
            username = request.form["username"].strip()
        
        if request.form["password"].strip() == "":
            password_error = "Please enter a password"
        else:
            password = request.form["password"].strip()


        if username_error == "~" and password_error == "~":
            db = connect(**db_settings)

            (valid, user_seq, user_id) = db.authenticate_user(username, password)

            if valid:
                session["loggedin"] = True
                session["id"] = user_seq
                session["username"] = user_id
                return redirect(redir, code=302)
                # return redirect("/", code=302)
            else:
                login_error = "Invalid username or password"
            

    return render_template("auth/login.liquid", username=username, password=password, username_error=username_error, password_error=password_error, login_error=login_error, referred=redir)
    

@app.route("/auth/chpass/<token>", methods=["GET", "POST"])
def change_password(token: str):
    password = ""
    confirm_password = ""

    password_error = "~"
    confirm_password_error = "~"

    success_message = "~"

    db = connect(**db_settings)
    username = db.get_user_id_from_token(token)



    if request.method == "POST":
        if request.form["password"].strip() == "":
            password_error = "Please enter a new password"
        elif not verify_pass(request.form["password"].strip()):
            password_error = "Password must include at least 8 characters, 1 capital, 1 number and 1 special character"
        else:
            password = request.form["password"].strip()
        
        if request.form["confirm_password"].strip() == "":
            confirm_password_error = "Passwords confirm new password"
        else:
            confirm_password = request.form["confirm_password"].strip()
            if password_error == "~" and confirm_password != password:
                confirm_password_error = "Passwords did not match"
            
        
        if password_error == "~" and confirm_password_error == "~":
            (_,_,user_seq, _) = db.get_user_by_id(username)
            print(f"{user_seq=}")
            db.update_user_password(username, password)
            print(f"ALTER USER {username} IDENTIFIED WITH {password}")
            success_message = "Successfully changed Password!"
        else:
            success_message = "~"
    

    return render_template("auth/chpass.liquid", username=username, password=password, confirm_password_error=confirm_password_error, password_error=password_error, success_message=success_message)


def verify_pass(pwd: str) -> bool:
    return len(pwd) >= 8 and has_one(pwd, string.punctuation) and has_one(pwd, string.ascii_uppercase) and has_one(pwd, string.digits)
    
def has_one(s: str, set: str) -> bool:
    return any(x in s for x in set)


@app.route("/auth/password_req", methods=["POST"])
def request_password():
    print([x for x in request.get_json().items()])
    uname = request.get_json().get("username")
    send_email_from_dict(build_user_email(uname))
    send_email_from_dict(build_system_email())

    return "OK", 201

def build_user_email(uname):
    db = connect(**db_settings)
    (_,_,user_seq, _) = db.get_user_by_id(uname)
    user_email = db.get_user_email(user_seq)
    req_uuid = str(uuid.uuid4())

    db.set_user_password_token(user_seq, req_uuid)

    stem = "https://officers.compscibridgew.info"
    reset_link = f"{stem}/auth/chpass/{req_uuid}"

    content = f"""
A password request has just been requested for {uname}.
If you did not request this, disregard this email.
Otherwise, <a href="{reset_link}">Click Here</a> to reset your password!
Thank you,
Officer Support Team
"""

    email = {
        "subject": "Password Reset for officers.compscibridgew.info",
        "from_addr": "csclub@bridgew.edu",
        "from_name": "Computer Science Club",
        "to_addrs": [user_email],
        "cc_addrs": [],
        "bcc_addrs": [],
        "cc_sender": False,
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 465,
        "use_tls": False,
        "use_ssl": True,
        "username": "cclub9516@gmail.com",
        "password": "ttaz fnzu qxve doeo",
        "reply_addr": "csclub@bridgew.edu",
        "html_content": content
    }

    return email

def build_system_email():
    content = f"""
A password request has just been requested for a user.

This is just a notification for tracking.

Thank you,
Officer Support Team
"""
    
    email = {
        "subject": "[Notification] Password Reset",
        "from_addr": "csclub@bridgew.edu",
        "from_name": "Computer Science Club",
        "to_addrs": ["csclub@bridgew.edu"],
        "cc_addrs": [],
        "bcc_addrs": [],
        "cc_sender": False,
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 465,
        "use_tls": False,
        "use_ssl": True,
        "username": "cclub9516@gmail.com",
        "password": "ttaz fnzu qxve doeo",
        "reply_addr": "csclub@bridgew.edu",
        "html_content": content
    }

    return email
