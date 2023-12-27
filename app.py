from flask import Flask, request, send_file, make_response
from flask_liquid import Liquid, render_template
import json

allowed_users = [
    "e19202b7da58a905db8c47f18774060a271a75c81e27dec05a2c5ffd195d3ec1c330a95" +
    "4097343a52627ec37ba280fa8b046152043675d6918fa92544bbc97b4",  # Alex D
    "0c6e79700db58be02f5a8777d4983ea4cfa2fd2964827f1931e9b3fc55ea32076be88fc" +
    "466444ea7433a9eb203b0e38278c20329164e2d21af83d9a6725168c6",  # Lyra B
    "5322332540bd0a3ff904369e3fa09e652230b6eb1135fd690f704ea524d5c0de5f5e060" +
    "cd96f2fd809f6761ad66738a869f8d8906be6ac49edaa54031ec6f7b0",  # Mila TG
    "8d85a6e835482f01fa73ced76b3df78199d1557de1aa4fcd84e84794fb3d2da1c6ba60b" +
    "29c7f44bd2f9fcc74e3c4cb6ba24ec9af0c3a6201374e51a67a6ec50f",  # Sean S
    "7ca8664800a00b6fcdbe86aa59eaf93d46d2ef8f0e040092dd441c6c26d3af3892d980d" +
    "ef05c8f474b0c1b68d30999615194417b079104352be524e816510dd9",  # Margaret B
    "16cfb0703eaeeffa680bd182226c2cc55f8cbc7062025a98b228b411c4f95cd1b5ab50d" +
    "4618667f03522171a7dda229c6b3f0ff82ceb1580e646149d05b51721"   # Alexis W
]

app = Flask(__name__)
liquid = Liquid(app)
app.config.update(
    LIQUID_TEMPLATE_FOLDER="./templates/",
)


def get_next_id():
    try:
        items = json.load(open("records.json"))
    except FileNotFoundError:
        return "Records File not found! Please contact your " + \
               "systems administrator", 500
    last_id = 0
    for item in items:
        if item.get("type") == "sga_budget":
            continue
        last_id = max(
            last_id,
            int(item.get("id"))
        )
    return str(last_id + 1)


@app.route("/")
def get_root():
    if request.cookies.get('userID') not in allowed_users:
        return "You are not allowed to access this page", 403
    try:
        items = json.load(open("records.json"))[1:]
    except FileNotFoundError:
        return "Records File not found!" + \
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

    return render_template("main.liquid", records=items)


@app.route("/view/")
def return_error_no_view():
    if request.cookies.get('userID') not in allowed_users:
        return "You are not allowed to access this page", 403
    return "Err: Invoice ID not supplied", 400


@app.route("/view/<ID>")
def view_item(ID=None):
    if request.cookies.get('userID') not in allowed_users:
        return "You are not allowed to access this page", 403
    if ID is None:
        return "Invoice ID not supplied", 400
    try:
        items = json.load(open("records.json"))
    except FileNotFoundError:
        return "Records File not found!" + \
               " Please contact your systems administrator", 500

    for item in items:
        if ID == item.get("id"):
            return render_template("invoice.liquid", **item)

    return "Item not found!", 404


@app.route('/logo')
def get_image():
    if request.cookies.get('userID') not in allowed_users:
        return "You are not allowed to access this page", 403
    return send_file("logo.jpg", mimetype='image/gif')


@app.route('/new/')
def create_inv():
    if request.cookies.get('userID') not in allowed_users:
        return "You are not allowed to access this page", 403
    return render_template("new_invoice.liquid", id=get_next_id())


@app.post("/new/")
def create_inv_post():
    if request.cookies.get('userID') not in allowed_users:
        return "You are not allowed to access this page", 403
    try:
        items = json.load(open("records.json"))
    except FileNotFoundError:
        return "Records File not found!" + \
            " Please contact your systems administrator", 500
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
    if request.cookies.get('userID') not in allowed_users:
        return "You are not allowed to access this page", 403
    if ID is None:
        return "Invoice ID not supplied", 400
    try:
        items = json.load(open("records.json"))
    except FileNotFoundError:
        return "Records File not found!" + \
               " Please contact your systems administrator", 500

    for item in items:
        if ID == item.get("id"):
            return render_template("edit_invoice.liquid", **item)

    return "Item not found!", 404


@app.patch("/edit/<ID>")
def edit_inv_post(ID=None):
    if request.cookies.get('userID') not in allowed_users:
        return "You are not allowed to access this page", 403
    if ID is None:
        return "Invoice ID not supplied", 400
    try:
        items = json.load(open("records.json"))
    except FileNotFoundError:
        return "Records File not found!" + \
               " Please contact your systems administrator", 500
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
    return f"Record edited with ID: {data.get('id')}", 201


@app.route("/set_user/<ID>")
def set_user(ID=None):
    if ID is None:
        return "User ID not supplied", 400
    if ID not in allowed_users:
        return "User ID not allowed", 403
    resp = make_response(f"User ID set to {ID}")
    resp.set_cookie('userID', ID)

    return resp, 200
