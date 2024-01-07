from app import app
from db_conn import connect
from flask import request, send_file, make_response
from flask_liquid import render_template
from db_config import db_settings
import json
import time

def load_docket():
    try:
        return json.load(open("docket.json", "r"))
    except FileNotFoundError:
        with open("docket.json", "w") as f:
            json.dump([], f)
        return []


def save_docket(docket):
    json.dump(docket, open("docket.json", "w"), indent=4)


@app.route("/docket/")
def get_docket_root():
    db = connect(**db_settings)
    if request.cookies.get('userID') not in db.get_available_users():
        return "You are not allowed to access this page", 403
    db.close()
    items = load_docket()
    return render_template("docket/main.liquid", docket_items=items)


@app.route("/docket/view/<ID>")
def view_docket_item(ID=None):
    db = connect(**db_settings)
    if request.cookies.get('userID') not in db.get_available_users():
        return "You are not allowed to access this page", 403
    if ID is None:
        return "Docket ID not supplied", 400
    db.close()
    items = load_docket()
    return render_template("docket/view.liquid", record=items[int(ID) - 1])

@app.post("/docket/new/")
def add_docket_item():
    db = connect(**db_settings)
    if request.cookies.get('userID') not in db.get_available_users():
        return "You are not allowed to access this page", 403
    user = db.get_user(request.cookies.get('userID'))
    db.close()
    items = load_docket()
    result = {
        key: val for key, val in request.form.items()
    }
    result["created_by"] = user
    result['docket_id'] = len(items) + 1
    result['status'] = "Open"
    result['create_date'] = int(time.time())
    items.append(result)
    save_docket(items)
    return "OK", 201


@app.post("/docket/edit/<ID>")
def edit_docket_item(ID=None):
    db = connect(**db_settings)
    if request.cookies.get('userID') not in db.get_available_users():
        return "You are not allowed to access this page", 403
    if ID is None:
        return "Docket ID not supplied", 400
    db.close()
    items = load_docket()
    items[int(ID) - 1] = request.form
    save_docket(items)
    return "OK", 201

@app.route("/docket/edit/<ID>")
def get_docket_exit(ID=None):
    db = connect(**db_settings)
    if request.cookies.get('userID') not in db.get_available_users():
        return "You are not allowed to access this page", 403
    user_info = db.get_user_full(request.cookies.get('userID'))
    db.close()
    print(user_info)
    items = load_docket()
    return render_template("docket/edit.liquid", record=items[int(ID) - 1], current_user=user_info)


@app.route("/docket/favicon.ico")
def docket_favicon():
    db = connect(**db_settings)
    if request.cookies.get('userID') not in db.get_available_users():
        return "You are not allowed to access this page", 403
    db.close()
    return send_file("./static/docket/favicon.ico", mimetype='image/gif')

@app.get("/docket/new/")
def create_docket():
    db = connect(**db_settings)
    if request.cookies.get('userID') not in db.get_available_users():
        return "You are not allowed to access this page", 403
    user_name = db.get_user(request.cookies.get('userID'))
    db.close()
    recordID = len(load_docket()) + 1

    return render_template("docket/new.liquid", user_name=user_name, recordID=recordID)

