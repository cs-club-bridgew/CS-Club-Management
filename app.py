from flask import Flask, request, send_file
from flask_liquid import Liquid, render_template
import json

app = Flask(__name__)
liquid = Liquid(app)
app.config.update(
    LIQUID_TEMPLATE_FOLDER="./templates/",
)

@app.route("/")
def get_root():
    try:
        items = json.load(open("records.json"))[1:]
    except FileNotFoundError:
        return "Records File not found! Please contact your systems administrator", 500
    return render_template("main.liquid", records=items)

@app.route("/view/")
def return_error_no_view():
    return "Err: Invoice ID not supplied", 400

@app.route("/view/<ID>")
def view_item(ID=None):
    if ID is None:
        return "Invoice ID not supplied", 400
    try:
        items = json.load(open("records.json"))
    except FileNotFoundError:
        return "Records File not found! Please contact your systems administrator", 500
    
    for item in items:
        if ID == item.get("id"):
            return render_template("invoice.liquid", **item)
    
    return "Item not found!", 404
    
    
@app.route('/logo')
def get_image():
    return send_file("logo.jpg", mimetype='image/gif')
    
@app.route('/new/')
def create_inv():
    
    return render_template("new_invoice.liquid")


@app.post("/new/")
def create_inv_post():
    try:
        items = json.load(open("records.json"))
    except FileNotFoundError:
        return "Records File not found! Please contact your systems administrator", 500
    # get the data from the json body
    data = request.get_json()
    # add the data to the items list
    items.append(data)
    # write the data to the file
    json.dump(items, open("records.json", "w"), indent=4)
    # return the ID
    return "Record created with ID: {}".format(data.get("id")), 201

@app.route("/edit/<ID>")
def edit_inv(ID=None):
    if ID is None:
        return "Invoice ID not supplied", 400
    try:
        items = json.load(open("records.json"))
    except FileNotFoundError:
        return "Records File not found! Please contact your systems administrator", 500
    
    for item in items:
        if ID == item.get("id"):
            return render_template("edit_invoice.liquid", **item)
    
    return "Item not found!", 404

@app.patch("/edit/<ID>")
def edit_inv_post(ID=None):
    if ID is None:
        return "Invoice ID not supplied", 400
    try:
        items = json.load(open("records.json"))
    except FileNotFoundError:
        return "Records File not found! Please contact your systems administrator", 500
    # get the data from the json body
    data = request.get_json()
    # add the data to the items list
    for item in items:
        if ID == item.get("id"):
            for key, value in data.items():
                item[key] = value
    # write the data to the file
    json.dump(items, open("records.json", "w"), indent=4)
    # return the ID
    return "Record edited with ID: {}".format(data.get("id")), 201