from flask import Flask, send_file, make_response
from flask_liquid import Liquid, render_template
from db_config import db_settings
from db_conn import connect


app = Flask(__name__)
liquid = Liquid(app)
app.config.update(
    LIQUID_TEMPLATE_FOLDER="./templates/",
)

import invoices
import docket

@app.route("/style.css")
def get_main_css():
    return send_file("static/style.css")

@app.route("/invoices/style.css")
def get_invoice_css():
    return send_file("static/invoice-main.css")

@app.route("/navbar/")
def get_navbar():
    return render_template("navbar.liquid")

@app.route("/about/")
def get_about():
    return render_template("about.liquid")

@app.route("/")
def get_main_root():
    return render_template("navbar.liquid")

@app.route("/blockFont.ttf")
def get_block_font():
    return send_file("static/PrintChar21.ttf")

@app.route("/set_user/<ID>")
def set_user(ID=None):
    db = connect(**db_settings)
    if ID is None:
        return "User ID not supplied", 400
    if ID not in db.get_available_users():
        return "User ID not allowed", 403
    resp = make_response(render_template("invoices/UserID.liquid", id=ID))
    resp.set_cookie('userID', ID)
    db.close()
    return resp, 200

@app.route("/set_user/")
def get_set_user():
    return """

<script> window.location.href=`/set_user/${prompt("Enter your User ID")}`</script>
"""