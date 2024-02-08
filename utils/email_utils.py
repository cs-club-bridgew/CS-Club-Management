import smtplib
from email.message import EmailMessage
from email.utils import make_msgid, formataddr
from routes.docket import load_docket, save_docket
import time
from utils.db_conn import connect
from db_config import db_settings
from bs4 import BeautifulSoup as bs
import json
from flask_liquid import render_template

def modify_email_attrs(msg: EmailMessage, data: dict) -> None:
    msg['Subject'] = data['subject']
    msg['From'] = formataddr((data['from_name'], data['from_addr']))
    msg['To'] = ', '.join(data['to_addrs'])
    msg['Cc'] = ', '.join(data['cc_addrs'])
    msg['Bcc'] = ', '.join(data['bcc_addrs'])
    msg.add_header('reply-to', data['reply_addr'])
    msg.set_content(bs(data['html_content'], "html.parser").text, 'plain')
    msg.add_alternative(data['html_content'], 'html')
    # msg.add_related(data['image'], 'image', 'png', cid=make_msgid()) 

def create_docket_item(invoice_id):
    db = connect(**db_settings)
    invoice = db.get_invoice_by_id(invoice_id)
    user = invoice['creator']
    db.close()
    items = load_docket()
    result = {}
    result['title'] = f"Review Financial Record #{invoice_id}"
    result['description'] = f"Review the financial record #{invoice_id} created by {user} on {invoice['date'].strftime('%m/%d/%Y')}."
    result["created_by"] = user
    result['docket_id'] = len(items) + 1
    result['status'] = "In Progess"
    result['create_date'] = time.mktime(invoice['date'].timetuple())
    result['href'] = f"/invoices/view/{invoice_id}"
    items.append(result)
    save_docket(items)
    
    
def send_item(msg, data):
    smtp_host = data['smtp_host'] + ":" + str(data['smtp_port'])
    if data['use_ssl']:
        s = smtplib.SMTP_SSL(smtp_host)
    else:
        s = smtplib.SMTP(smtp_host)
    if data['use_tls']:
        s.starttls()
    s.login(data['username'], data['password'])
    
    to_addrs = data['to_addrs']
    cc_addrs = data['cc_addrs']
    bcc_addrs = data['bcc_addrs']
    from_addr = data['from_addr']
    to_list = to_addrs + cc_addrs + bcc_addrs
    s.sendmail(from_addr, to_list, msg.as_string())
    s.quit()
    
def send_email_from_file(email_file: str):
    email_content = json.load(open(email_file))
    send_email_from_dict(email_content)

def send_email_from_dict(email_content: dict):
    msg = EmailMessage()
    modify_email_attrs(msg, email_content)
    send_item(msg, email_content)