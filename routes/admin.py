from app import app
from utils.db_conn import connect
from flask import request, send_file, make_response
from flask_liquid import render_template
from db_config import db_settings

@app.route("/admin/users/")
def manageUsers():
    user_id = request.cookies.get('userID')
    db = connect(**db_settings)
    db.is_user_app_admin(user_id)
    users = db.get_users()
    db.close()
    return render_template("admin/users.liquid", users=users)

@app.route("/admin/perms/")
def managePermissions():
    user_id = request.cookies.get('userID')
    db = connect(**db_settings)
    db.is_user_app_admin(user_id)
    perms = db.get_all_user_perms()
    db.close()
    return render_template("admin/permissions.liquid", perms=perms)

@app.route("/admin/users/create", methods=["GET"])
def createUser():
    user_id = request.cookies.get('userID')
    db = connect(**db_settings)
    db.is_user_app_admin(user_id)
    db.close()
    return render_template("admin/create.liquid")

@app.route("/admin/users/create", methods=["POST"])
def createUserPost():
    user_id = request.cookies.get('userID')
    db = connect(**db_settings)
    db.is_user_app_admin(user_id)
    try:
        userSeq = db.create_user(request.form)
        print(request.form)
        db.create_user_perms(userSeq, request.form)
        db.close()
    except Exception as e:
        print(e)
        return "User creation failed"
    return "User created"
