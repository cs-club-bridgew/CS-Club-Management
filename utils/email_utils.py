import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
import mimetypes
from typing import List
from email import encoders
from pathlib import Path
from routes.docket import load_docket, save_docket
import time
from utils.db_conn import connect
from db_config import db_settings, email_settings
import pdfkit 
from bs4 import BeautifulSoup


def send_email(subject, message, from_addr, to_addrs, cc_addrs, bcc_addrs, smtp_host, username, password, attachments=[], reply_addr = "", use_tls=False, use_ssl=True):
    
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = ", ".join(to_addrs)
    msg['Cc'] = ", ".join(cc_addrs) + f", {from_addr}" # Always CC the sender for record keeping.
    msg['Bcc'] = ", ".join(bcc_addrs)
    
    if reply_addr != "":
        msg.add_header('reply-to', reply_addr)
    
    # Set the message text content
    msg.set_content(BeautifulSoup(message, "html.parser").text, 'plain')
    
    image_cid = make_msgid(domain='xyz.com')
    
    msg.add_alternative(message.format(image_cid=image_cid[1:-1]), 'html')
    
    with open('static/invoices/logo.jpg', 'rb') as img:

        # know the Content-Type of the image
        maintype, subtype = mimetypes.guess_type(img.name)[0].split('/')

        # attach it
        msg.get_payload()[1].add_related(img.read(), 
                                            maintype=maintype, 
                                            subtype=subtype, 
                                            cid=image_cid)
    
    
    if use_ssl:
        s = smtplib.SMTP_SSL(smtp_host)
    else:
        s = smtplib.SMTP(smtp_host)
    if use_tls:
        s.starttls()
    # s.login(username, password)
    to_list = to_addrs + cc_addrs + bcc_addrs
    s.sendmail(from_addr, to_list, msg.as_string())
    s.quit()
    
def convert_url_to_pdf(url, pdf_path):
    options = {
        'page-height': '11in',
        'page-width': '8.5in',
        'cookie': [('userID', '~'), ('printing', '1')]
    }
    pdfkit.from_url(url, pdf_path, options=options) 


def format_lines(lines: list) -> str:
    headers = ["Item", "Description", "Quantity", "Unit Price", "Total"]
    col_widths = [len(x) for x in headers]
    
    for line in lines:
        for i, col in enumerate(line.values()):
            col_widths[i] = max(col_widths[i], len(str(col)))
    col_widths = [width + 4 for width in col_widths]
    ret_str = "<pre>"
    
    
    for i, item in enumerate(headers):
        ret_str += f"{item:^{col_widths[i]}}"
    ret_str += "<br/>"
    
    for line in lines:
        for i, col in enumerate(line.values()):
            ret_str += f"{col:^{col_widths[i]}}"
        ret_str += "<br/>"
        
    return ret_str + "</pre>"

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
    return "<DOCTYPE html><html><meta http-equiv='refresh' content='0; url=/docket/'/></html>", 201


def alert_users_of_new_invoice(invoice_id):
    db = connect(**db_settings)
    invoice = db.get_invoice_by_id(invoice_id)
    subject = f"New Financial Record: {invoice['type']} #{invoice_id}"
    address = '\n'.join(invoice['return_addr'])
    lines = format_lines(invoice['li'])
    
    message_body = f"""
<html>
    <head></head>
    <body>
        <font face="Courier New, Courier, monospace">
        <img src="cid:{{image_cid}}" alt="BSU Logo" style="width: 150px;"/><br/>
        Hello,<br/>
        A new invoice has been created by {invoice['creator']} and is awaiting approval from an authorized user.<br/><br/>

        Invoice Details:<br/>
        Record ID: {invoice_id}<br/>
        Total Lines: {len(invoice['li'])}<br/>
        Created By: {invoice['creator']}<br/>
        Created On: {invoice['date']}<br/>
        Invoice Address:<br/>
        {address}<br/><br/>

        Line Details:<br/>
        {lines}<br/><br/>

        Taxes: ${invoice['tax']}<br/>
        Fees: ${invoice['fees']}<br/>
        Total: ${invoice['total']}<br/><br/>

        A officer docket item has been generated to review this invoice.<br/><br/>

        This is an automated email sent from a shared inbox. If you have any questions, please reach out to csclub@bridgew.edu.
    </font>
    </body>
</html>
    """
    email_recip = db.get_approver_emails()
    db.close()
    
    
    send_email(subject, message_body, 
              "csclub@bridgew.edu", email_recip,
              [], [], email_settings["smtp_host"], email_settings['username'],
              email_settings['password'], use_ssl=False)
    
def alert_users_of_updated_invoice(invoice_id):
    db = connect(**db_settings)
    invoice = db.get_invoice_by_id(invoice_id)
    subject = f"New Financial Record: {invoice['type']} #{invoice_id}"
    address = '\n'.join(invoice['return_addr'])
    lines = format_lines(invoice['li'])
    
    message_body = f"""
<html>
    <head></head>
    <body>
        <font face="Courier New, Courier, monospace">
        <img src="cid:{{image_cid}}" alt="BSU Logo" style="width: 150px;"/><br/>

        Hello,<br/>
        An invoice has been updated. The invoice was created by {invoice['creator']} and is awaiting approval from an authorized user.<br/><br/>

        Invoice Details:<br/>
        Record ID: {invoice_id}<br/>
        Total Lines: {len(invoice['li'])}<br/>
        Created By: {invoice['creator']}<br/>
        Created On: {invoice['date']}<br/>
        Invoice Address:<br/>
        {address}<br/><br/>

        Line Details:<br/>
        {lines}<br/><br/>

        Taxes: ${invoice['tax']}<br/>
        Fees: ${invoice['fees']}<br/>
        Total: ${invoice['total']}<br/><br/>

        A officer docket item has been generated to review this invoice.<br/><br/>

        This is an automated email sent from a shared inbox. If you have any questions, please reach out to csclub@bridgew.edu.
    </font>
    </body>
</html>
    """
    email_recip = db.get_approver_emails()
    db.close()
    
    
    send_email(subject, message_body, 
              "csclub@bridgew.edu", email_recip,
              [], [], email_settings["smtp_host"], email_settings['username'],
              email_settings['password'] , use_ssl=False)
    
def alert_invoice_new(invoice_id):
    # convert_url_to_pdf(f'https://officers.compscibridgew.info/invoices/view/{invoice_id}', f'Invoice{invoice_id}.pdf')
    alert_users_of_new_invoice(invoice_id)
    create_docket_item(invoice_id)
    
    
def alert_invoice_update(invoice_id):
    # convert_url_to_pdf(f'https://officers.compscibridgew.info/invoices/view/{invoice_id}', f'Invoice{invoice_id}.pdf')
    alert_users_of_updated_invoice(invoice_id)
    create_docket_item(invoice_id)