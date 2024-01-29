from app import app
from flask import request
from db_config import db_settings
from db_conn_old import connect

@app.post("/invoice/address/new/")
def create_address():
    db = connect(**db_settings)
    if request.cookies.get('userID') not in db.get_available_users():
        return "You are not allowed to access this page", 403
    db.close()