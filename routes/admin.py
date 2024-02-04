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
    return render_template("admin/users/main.liquid", users=users)

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
    return render_template("admin/users/create.liquid")

@app.route("/admin/users/create", methods=["POST"])
def createUserPost():
    user_id = request.cookies.get('userID')
    db = connect(**db_settings)
    db.is_user_app_admin(user_id)
    try:
        userSeq = db.create_user(request.form)
        db.create_user_perms(userSeq, request.form)
        db.close()
    except Exception as e:
        print(e)
        return "<script>alert('Error creating user'); window.location.href = '/admin/users/create';</script>"
    return "<script>alert('User Created'); window.location.href = '/admin/users';</script>"

@app.route("/admin/users/edit/<int:user_seq>", methods=["GET"])
def editUser(user_seq):
    user_id = request.cookies.get('userID')
    db = connect(**db_settings)
    db.is_user_app_admin(user_id)
    user = db.get_all_user_info(user_seq)
    db.close()
    return render_template("admin/users/edit.liquid", user=user, seq=user_seq)

@app.route("/admin/users/edit/<int:user_seq>", methods=["POST"])
def editUserPost(user_seq):
    user_id = request.cookies.get('userID')
    db = connect(**db_settings)
    db.is_user_app_admin(user_id)
    resp = make_response()
    try:
        data = request.form.to_dict()
        db.update_user_info(user_seq, data)
        db.update_user_perms(user_seq, data)
        # If the userID is the same as the user we are updating, reload their theme cookie.
        if user_id == db.get_user_id(user_seq):
            resp.set_cookie("themeID", data.get("theme", 1))
        resp.data = "<script>alert('User updated'); window.location.href = '/admin/users';</script>"
        db.close()
    except Exception as e:
        print(e)
        resp.data = f"<script>alert('Error updating user'); window.location.href = '/admin/users/edit/{user_seq}';</script>"
        resp.status_code = 500
    return resp

@app.get("/admin/addresses/")
def view_addresses():
    user_id = request.cookies.get('userID')
    db = connect(**db_settings)
    db.is_user_app_admin(user_id)
    addresses = db.get_available_addresses()
    return render_template("admin/addresses/main.liquid", addresses=addresses)

@app.get("/admin/addresses/edit/<int:addrSeq>")
def editAddress(addrSeq: int):
    user_id = request.cookies.get('userID')
    db = connect(**db_settings)
    db.is_user_app_admin(user_id)
    addr_data = db.get_address_by_seq(addrSeq)
    db.close()
    return render_template("admin/addresses/edit.liquid", addr_data=addr_data)

@app.post("/admin/addresses/edit/<int:addrSeq>")
def editAddressPost(addrSeq: int):
    user_id = request.cookies.get('userID')
    db = connect(**db_settings)
    db.is_user_app_admin(user_id)
    try:
        db.update_address(addrSeq, request.form.to_dict())
        db.close()
    except Exception as e:
        db.close()
        print(e)
        return f"<script>alert('Error updating address'); window.location.href = '/admin/addresses/edit/{addrSeq}';</script>"
    return "<script>alert('Address Updated'); window.location.href = '/admin/addresses';</script>"

@app.get("/admin/addresses/new")
def new_address():
    user_id = request.cookies.get('userID')
    db = connect(**db_settings)
    db.is_user_app_admin(user_id)
    db.close()
    return render_template("admin/addresses/new.liquid")

@app.post("/admin/addresses/new")
def new_address_post():
    user_id = request.cookies.get('userID')
    db = connect(**db_settings)
    db.is_user_app_admin(user_id)
    try:
        req_dict = request.form.to_dict()
        addr_info = [
            req_dict['line1'],
            req_dict['line2'],
            req_dict['line3'],
            req_dict['line4']
        ]
        db.create_address(addr_info, req_dict['desc'])
        db.close()
    except Exception as e:
        db.close()
        print(e)
        return f"<script>alert('Error creating address'); window.location.href = '/admin/addresses/new';</script>"
    return "<script>alert('Address Created'); window.location.href = '/admin/addresses';</script>"

@app.get("/admin/record/")
def record_main():
    user_id = request.cookies.get('userID')
    db = connect(**db_settings)
    db.is_user_app_admin(user_id)
    records = db.get_all_type_info()
    return render_template("admin/record/main.liquid", records=records)

@app.post("/admin/record/edit/<int:record_seq>")
def record_edit_post(record_seq: int):
    user_id = request.cookies.get('userID')
    db = connect(**db_settings)
    db.is_user_app_admin(user_id)
    try:
        json_data = request.get_json().get('description')
        if json_data is None:
            raise Exception("No data provided")
        db.update_type_info(record_seq, json_data)
        db.close()
    except Exception as e:
        db.close()
        print(e)
        return f"<script>alert('Error updating record'); window.location.href = '/admin/record';</script>", 500
    return "<script>alert('Record Updated'); window.location.href = '/admin/record';</script>", 200

@app.post("/admin/record/new")
def record_new_post():
    user_id = request.cookies.get('userID')
    db = connect(**db_settings)
    db.is_user_app_admin(user_id)
    try:
        json_data = request.get_json().get('description')
        if json_data is None:
            raise Exception("No data provided")
        db.create_type(json_data)
        db.close()
    except Exception as e:
        db.close()
        print(e)
        return f"<script>alert('Error creating record'); window.location.href = '/admin/record';</script>", 500
    return "<script>alert('Record Created'); window.location.href = '/admin/record';</script>", 200

@app.get("/admin/status/")
def view_statuses():
    user_id = request.cookies.get('userID')
    db = connect(**db_settings)
    db.is_user_app_admin(user_id)
    statuses = db.get_status_info()
    return render_template("admin/status/main.liquid", statuses=statuses)

@app.post("/admin/status/edit/<int:status_seq>")
def editStatusPost(status_seq: int):
    user_id = request.cookies.get('userID')
    db = connect(**db_settings)
    db.is_user_app_admin(user_id)
    try:
        json_data = request.get_json().get('description')
        if json_data is None:
            raise Exception("No data provided")
        db.update_status_info(status_seq, json_data)
        db.close()
    except Exception as e:
        db.close()
        print(e)
        return f"<script>alert('Error updating status'); window.location.href = '/admin/status';</script>", 500
    return "<script>alert('Status Updated'); window.location.href = '/admin/status';</script>", 200

@app.post("/admin/status/new")
def newStatusPost():
    user_id = request.cookies.get('userID')
    db = connect(**db_settings)
    db.is_user_app_admin(user_id)
    try:
        json_data = request.get_json().get('description')
        if json_data is None:
            raise Exception("No data provided")
        db.create_status(json_data)
        db.close()
    except Exception as e:
        db.close()
        print(e)
        return f"<script>alert('Error creating status'); window.location.href = '/admin/status';</script>", 500
    return "<script>alert('Status Created'); window.location.href = '/admin/status';</script>", 200
