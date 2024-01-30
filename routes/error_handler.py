from app import app
import utils.app_utils as app_utils
from flask_liquid import render_template

@app.errorhandler(app_utils.UserAccessInvoiceNoEditException)
@app.errorhandler(app_utils.UserAccessDocketNoEditException)
def user_no_inv_edit(e):
    return render_template("exceptions/UserAccessInvoiceNoEditException.liquid"), 403

@app.errorhandler(app_utils.UserAccessInvoiceNoReadException)
@app.errorhandler(app_utils.UserAccessDocketNoReadException)
def user_no_inv_edit(e):
    return render_template("exceptions/UserAccessInvoiceNoReadException.liquid"), 403


@app.errorhandler(app_utils.UserAccessNotSignedInException)
def user_no_userid(e):
    return render_template("exceptions/UserAccessNotSignedIn.liquid"), 403