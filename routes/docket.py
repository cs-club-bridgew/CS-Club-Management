from app import app
from utils.db_conn import connect
from flask import request, send_file, make_response
from flask_liquid import render_template
from db_config import db_settings
import json
import time
import utils.app_utils
from utils.docket_report import generate_docket_report

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
    db.can_user_view_docket(request.cookies.get('userID'))
    db.close()
    items = load_docket()
    return render_template("docket/main.liquid", docket_items=items)


@app.route("/docket/view/<ID>")
def view_docket_item(ID=None):
    db = connect(**db_settings)
    db.can_user_view_docket(request.cookies.get('userID'))
    db.close()
    items = load_docket()
    record = items[int(ID) - 1]
    record['description'] = record['description'].split("\n")
    return render_template("docket/view.liquid", record=record)

@app.post("/docket/new/")
def add_docket_item():
    db = connect(**db_settings)
    db.can_user_edit_docket(request.cookies.get('userID'))
    user = db.get_user_name(request.cookies.get('userID'))
    db.close()
    items = load_docket()
    result = {
        key: val for key, val in request.form.items()
    }
    result["created_by"] = user
    result['docket_id'] = len(items) + 1
    result['status'] = "In Progess"
    result['create_date'] = int(time.time())
    items.append(result)
    save_docket(items)
    return "<DOCTYPE html><html><meta http-equiv='refresh' content='0; url=/docket/'/></html>", 201


@app.post("/docket/edit/<ID>")
def edit_docket_item(ID=None):
    db = connect(**db_settings)
    db.can_user_edit_docket(request.cookies.get('userID'))
    
    db.close()
    items = load_docket()
    item = items[int(ID) - 1]
    for key, val in request.form.items():
        item[key] = val
        if key == "status":
            match val:
                case '1':
                    item['status'] = "In Progress"
                case '2':
                    item['status'] = "Complete"
                case _:
                    item['status'] = "In Progress"
    in_fav = '0' if item.get("in_favor", "0") == '' else item.get("in_favor", "0")
    opposed = '0' if item.get("opposed", "0") == '' else item.get("opposed", "0")
    
    item["total"] = int(in_fav) + int(opposed)
    save_docket(items)
    return "<DOCTYPE html><html><meta http-equiv='refresh' content='0; url=/docket/'/></html>", 201


@app.route("/docket/edit/<ID>")
def get_docket_exit(ID=None):
    db = connect(**db_settings)
    db.can_user_edit_docket(request.cookies.get('userID'))
    user_info = db.get_user_name(request.cookies.get('userID'))
    try:
        is_doc_admin = db.is_user_docket_admin(request.cookies.get("userID"))
    except utils.app_utils.UserAccessDocketNoAdminException:
        is_doc_admin = False
    db.close()
    items = load_docket()
    if items[int(ID) - 1]["created_by"] == user_info or is_doc_admin:
        return render_template("docket/edit.liquid", record=items[int(ID) - 1], isAdmin=is_doc_admin)
    else:
        raise utils.app_utils.UserAccessDocketNoEditException

@app.route("/docket/favicon.ico")
def docket_favicon():
    db = connect(**db_settings)
    db.can_user_view_docket(request.cookies.get('userID'))
    db.close()
    return send_file("./static/docket/favicon.ico", mimetype='image/gif')


@app.get("/docket/new/")
def create_docket():
    db = connect(**db_settings)
    db.can_user_edit_docket(request.cookies.get('userID'))
    user_name = db.get_user_name(request.cookies.get('userID'))
    db.close()
    recordID = len(load_docket()) + 1

    return render_template("docket/new.liquid", user_name=user_name, recordID=recordID)


@app.get("/docket/report/<START>/<END>")
def gen_report(START=None, END=None):
    db = connect(**db_settings)
    db.can_user_view_docket(request.cookies.get('userID'))

    if START is None or END is None:
        return "Start and end dates not supplied", 400
    user = db.get_user_full(request.cookies.get('userID'))
    db.close()

    items = load_docket()
    
    for item in items[::-1]:
        
        if int(item['create_date']) < int(START) or int(item['create_date']) > int(END):
            items.remove(item)
        item['create_date'] = time.strftime("%m/%d/%Y", time.localtime(int(item['create_date'])))
    return send_file(generate_docket_report(items, time.strftime("%m/%d/%Y", time.localtime(int(START))), time.strftime("%m/%d/%Y", time.localtime(int(END))), user[1]))
