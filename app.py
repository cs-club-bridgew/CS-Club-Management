from flask import Flask, request, send_file, make_response
from flask_liquid import Liquid, render_template
from db_conn import connect
from sqlite3 import DatabaseError, ProgrammingError, IntegrityError, Error, InterfaceError
from db_config import db_settings


app = Flask(__name__)
liquid = Liquid(app)
app.config.update(
    LIQUID_TEMPLATE_FOLDER="./templates/",
)

def get_next_id():
    db = connect(**db_settings)
    next_id = db.get_next_invoice_id()
    db.close()
    return next_id

def get_available_addresses():
    db = connect(**db_settings)
    addresses = db.get_available_addresses()
    db.close()
    return addresses


@app.route("/")
def get_root():
    db = connect(**db_settings)
    if request.cookies.get('userID') not in db.get_available_users():
        return "You are not allowed to access this page", 403
    try:
        items = db.get_records()
    except (DatabaseError, ProgrammingError, IntegrityError, Error, InterfaceError):
        db.close()
        return "A database error has occured!" + \
               " Please contact your systems administrator", 500
    # Get the name of the column to sort by
    sort_by = request.args.get("sort", "id")
    is_asc = request.args.get("order", "asc") == "asc"
    if sort_by == "item_count":
        items = sorted(items,
                       key=lambda x: len(x.get("li")),
                       reverse=not is_asc)
    else:
        items = sorted(items, key=lambda x: x.get(sort_by), reverse=not is_asc)
        
        
    # Get filters
    exclude_types = request.args.get("excludeType", "").split(",")
    exclude_status = request.args.get("excludeStatus", "").split(",")

    for item in items[::-1]:
        if item.get("type") in exclude_types:
            items.remove(item)
        if item.get("status") in exclude_status:
            items.remove(item)
    db.close()
    return render_template("main.liquid", records=items)



@app.route("/view/<ID>")
def view_item(ID=None):
    db = connect(**db_settings)
    
    if request.cookies.get('userID') not in db.get_available_users():
        return "You are not allowed to access this page", 403
    if ID is None:
        return "Invoice ID not supplied", 400
    items = db.get_records()
    db.close()
    
    for item in items:
        if ID == str(item.get("id")):
            return render_template("invoice.liquid", **item)

    return "Item not found!", 404


@app.route('/logo')
def get_image():
    db = connect(**db_settings)
    if request.cookies.get('userID') not in db.get_available_users():
        db.close()
        return "You are not allowed to access this page", 403
    db.close()
    return send_file("logo.jpg", mimetype='image/gif')


@app.route('/new/')
def create_inv():
    db = connect(**db_settings)
    if request.cookies.get('userID') not in db.get_available_users():
        db.close()
        return "You are not allowed to access this page", 403
    db.close()
    addresses = get_available_addresses()
    return render_template("new_invoice.liquid", id=get_next_id(), valid_addr = addresses)


@app.post("/new/")
def create_inv_post():
    db = connect(**db_settings)
    if request.cookies.get('userID') not in db.get_available_users():
        db.close()
        return "You are not allowed to access this page", 403
    
    # get the data from the json body
    data = request.get_json()
    # add the data to the items list
    try:
        db.create_record(**data)
        lines = data.get("li")
        # update the lines, and add new ones if needed
        for lineIDX, line in enumerate(lines):
            db.create_item(data.get("id"), **line)
    except (DatabaseError, ProgrammingError, IntegrityError, Error, InterfaceError) as e:
        db.close()
        raise e
    # return the ID
    db.close()
    return "Record created with ID: {}".format(data.get("id")), 201


@app.route("/edit/<ID>")
def edit_inv(ID=None):
    db = connect(**db_settings)
    if request.cookies.get('userID') not in db.get_available_users():
        return "You are not allowed to access this page", 403
    if ID is None:
        return "Invoice ID not supplied", 400
    try:
        item = db.get_record_by_id(ID)
    except (DatabaseError, ProgrammingError, IntegrityError, Error, InterfaceError):
        return "Records File not found!" + \
               " Please contact your systems administrator", 500
    db.close()
    if item is not None:
        addresses = get_available_addresses()
        return render_template("edit_invoice.liquid", **item, valid_addr=addresses)

    return "Item not found!", 404


@app.patch("/edit/<ID>")
def edit_inv_post(ID=None):
    if request.cookies.get('userID') not in db.get_available_users():
        return "You are not allowed to access this page", 403
    if ID is None:
        return "Invoice ID not supplied", 400
    # get the data from the json body
    data = request.get_json()
    db = connect(**db_settings)
    # add the data to the items list
    try:
        db.update_record(**data)
        lines = data.get("li")
        # update the lines, and add new ones if needed
        for lineIDX, line in enumerate(lines):
            
            db.update_line(ID, lineIDX + 1, **line)
        # return the ID
        db.close()
        return f"Record edited with ID: {data.get('id')}", 201
    except (DatabaseError, ProgrammingError, IntegrityError, Error, InterfaceError) as e:
        db.close()
        return f"Error: {e}", 500
    
@app.route("/set_user/<ID>")
def set_user(ID=None):
    db = connect(**db_settings)
    if ID is None:
        return "User ID not supplied", 400
    if ID not in db.get_available_users():
        return "User ID not allowed", 403
    resp = make_response(render_template("UserID.liquid", id=ID))
    resp.set_cookie('userID', ID)
    db.close()
    return resp, 200

@app.route("/favicon.ico")
def favicon():
    return send_file("favicon.ico", mimetype='image/gif')


@app.post("/preview")
def preview():
    db = connect(**db_settings)
    if request.cookies.get('userID') not in db.get_available_users():
        db.close()
        return "You are not allowed to access this page", 403
    data = request.get_json()
    return render_template("invoice.liquid", **data)