from flask import Flask, request, send_file, make_response
from flask_liquid import Liquid, render_template
from db_conn import connect
from db_config import db_settings


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