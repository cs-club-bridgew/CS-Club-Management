from flask import Flask, send_file, make_response, request
from flask_liquid import Liquid, render_template
from db_config import db_settings
from db_conn import connect
import app_utils

app = Flask(__name__)
liquid = Liquid(app)
app.config.update(
    LIQUID_TEMPLATE_FOLDER="./templates/",
)

import invoices
import docket
import error_handler

@app.route("/style.css")
def get_main_css():
    return send_file("static/style.css")

@app.route("/invoices/style.css")
def get_invoice_css():
    return send_file("static/invoice-main.css")

@app.route("/invoices/invUtils.js")
def get_invoice_utils():
    return send_file("static/invoices/invUtils.js")

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
    db.is_user_valid(ID)
    resp = make_response(render_template("invoices/UserID.liquid", id=ID))
    resp.set_cookie('userID', ID)
    db.close()
    return resp, 200

@app.route("/set_user/")
def get_set_user():
    return """

<script> window.location.href=`/set_user/${prompt("Enter your User ID")}`</script>
"""
@app.route("/get_user_name/<ID>")
def get_user(ID=None):
    db = connect(**db_settings)
    user_name = db.get_user_name(ID)
    db.close()
    return user_name
