from app import app
from utils.db_conn import connect
from db_config import db_settings
from flask import request, send_file
from flask_liquid import render_template
# from utils.email_utils import alert_invoice_new, alert_invoice_update



@app.route("/invoices/")
def get_root():
    
    db = connect(**db_settings)
    userID = request.cookies.get('userID')
    db.is_user_valid(userID)
    db.can_user_view_invoice(userID)
    
    items = db.get_records()
    
    
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
    return render_template("invoices/main.liquid", records=items)



@app.route("/invoices/view/<ID>")
def view_item(ID=None):
    db = connect(**db_settings)
    userID = request.cookies.get('userID')
    db.is_user_valid(userID)
    
    db.can_user_view_invoice(request.cookies.get('userID'))
    
    
    items = db.get_records()
    db.close()

    for item in items:
        if ID == str(item.get("id")):
            return render_template("invoices/invoice.liquid", **item)

    return "Item not found!", 404


@app.route('/invoices/logo.jpg')
def get_image():
    db = connect(**db_settings)
    db.is_user_valid(request.cookies.get('userID'))
    db.close()
    return send_file("static/invoices/logo.jpg", mimetype='image/gif')


@app.route('/invoices/new/')
def create_inv():
    db = connect(**db_settings)
    db.is_user_valid(request.cookies.get('userID'))
    
    db.can_user_edit_invoice(request.cookies.get('userID'))
    addresses = db.get_available_addresses()
    statuses = db.get_available_statuses()
    types = db.get_available_types()
    next_id = db.get_next_invoice_id()
    db.close()
    return render_template("invoices/new_invoice.liquid",
                            valid_addr=addresses,
                            valid_statuses=statuses,
                            valid_types=types,
                            id=next_id,
                            current_user=request.cookies.get('userID'))


@app.post("/invoices/new/")
def create_inv_post():
    db = connect(**db_settings)
    db.is_user_valid(request.cookies.get('userID'))
    db.can_user_edit_invoice(request.cookies.get('userID'))
    
    # get the data from the json body
    data = request.get_json()
    print(data)
    # add the data to the items list
    # try:
    results = db.create_invoice(**data)
    if results[2]:
        # Send email
        alert_invoice_new(results[0])
    
    # return the ID
    db.close()
    return "Record created with ID: {}".format(data.get("id")), 201


@app.route("/invoices/edit/<ID>")
def edit_inv(ID=None):
    db = connect(**db_settings)
    
    db.is_user_valid(request.cookies.get('userID'))
    if ID is None:
        return "Invoice ID not supplied", 400
    db.can_user_edit_invoice(request.cookies.get('userID'))
    
    try:
        item = db.get_invoice_by_id(ID)
    except Exception as e:
        return "Records File not found!" + \
               " Please contact your systems administrator", 500
    if item is not None:
        addresses = db.get_available_addresses()
        statuses = db.get_available_statuses()
        types = db.get_available_types()
        db.close()
        return render_template("invoices/edit_invoice.liquid", **item,
                               valid_addr=addresses,
                               valid_statuses=statuses,
                               valid_types=types)
    db.close()

    return "Item not found!", 404


@app.patch("/invoices/edit/<ID>")
def edit_inv_post(ID=None):
    db = connect(**db_settings)

    db.is_user_valid(request.cookies.get('userID'))
    if ID is None:
        return "Invoice ID not supplied", 400
    db.can_user_edit_invoice(request.cookies.get('userID'))
    
    
    # get the data from the json body
    data = request.get_json()
    # add the data to the items list
    try:
        seq = db.update_record(**data)
        db.close()
        if seq == -1:
            return "Record not updated!", 404
        if seq == 1:
            # Send email
            alert_invoice_update(ID)
        return f"Record edited with ID: {data.get('id')}", 201
    except Exception as e:
        db.close()
        raise e
        # return f"Error: {e}", 500


@app.route("/invoices/favicon.ico")
def inv_favicon():
    return send_file("./static/invoices/favicon.ico", mimetype='image/gif')


@app.post("/invoices/preview")
def preview():
    db = connect(**db_settings)
    db.is_user_valid(request.cookies.get('userID'))
    data = request.get_json()
    return render_template("invoices/invoice.liquid", **data)
