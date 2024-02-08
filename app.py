from flask import Flask, send_file, make_response, request
from flask_liquid import Liquid, render_template
from db_config import db_settings
from utils.db_conn import connect


app = Flask(__name__)
liquid = Liquid(app)
app.config.update(
    LIQUID_TEMPLATE_FOLDER="./templates/",
)

import routes.invoices
import routes.docket
import routes.error_handler
import routes.admin
import utils.email_utils

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
    userAdmin = False
    db = connect(**db_settings)
    if request.cookies.get('userID'):
        try:
            userAdmin = db.is_user_admin(request.cookies.get('userID'))
        except:
            pass
    return render_template("navbar.liquid", isUserAdmin=userAdmin)

@app.route("/about/")
def get_about():
    return render_template("about.liquid")

@app.route("/")
def get_main_root():
    return get_navbar()

@app.route("/blockFont.ttf")
def get_block_font():
    return send_file("static/PrintChar21.ttf")

@app.route("/set_user/<ID>")
def set_user(ID=None):
    if ID == '~':
        raise app_utils.UserAccessNotSignedInException
    db = connect(**db_settings)
    db.is_user_valid(ID)
    theme = db.get_user_color_theme(ID)
    resp = make_response(render_template("invoices/UserID.liquid", id=ID))
    resp.set_cookie('userID', ID)
    resp.set_cookie('themeID', str(theme[0]))
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

@app.get("/utils.js")
def getUtilsJS():
    return send_file("static/utils.js")


@app.get("/1.css")
def get_theme_1():
    return send_file("static/themes/1.css")

@app.get("/2.css")
def get_theme_2():
    return send_file("static/themes/2.css")

if __name__ == "__main__":
   with app.app_context():
        print(render_template("invoices/main.liquid", **{
            "id": str(invoice[0]),
            "date": "10/22/2024",
            "creator": "Alex Dasneves",
            "approver": "",
            "type": "invoice",
            "tax": 0.00,
            "fees": 0.00,
            "total": 10.00,
            "status": "pending",
            "li": [
                {
                    "line": "1",
                    "desc": "",
                    "ammt": line[2],
                    "qty": line[3],
                    "total": line[4]
                } for line in lines
            ],
            "return_addr": [
                invoice[5],
                invoice[6],
                invoice[7],
                invoice[8]
                ]
                }))