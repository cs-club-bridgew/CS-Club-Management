import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from typing import List
from email import encoders
from pathlib import Path
from routes.docket import load_docket, save_docket
import time
from utils.db_conn import connect
from db_config import db_settings, email_settings
import pdfkit 


def send_email(subject, message, from_addr, to_addrs, cc_addrs, bcc_addrs, smtp_host, username, password, attachments=[], use_tls=False, use_ssl=True):
    
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = ", ".join(to_addrs)
    msg['Cc'] = ", ".join(cc_addrs)
    msg['Bcc'] = ", ".join(bcc_addrs)
    for path in attachments:
        part = MIMEBase('application', "octet-stream")
        with open(path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        f'attachment; filename="{Path(path).name}"')
        msg.attach(part)
    # Set the message text content
    msg.attach(MIMEText(message, 'plain'))
    
    if use_ssl:
        s = smtplib.SMTP_SSL(smtp_host)
    else:
        s = smtplib.SMTP(smtp_host)
    if use_tls:
        s.starttls()
    s.login(username, password)
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
    ret_str = ""
    
    
    for i, item in enumerate(headers):
        ret_str += f"{item:^{col_widths[i]}}"
    ret_str += "\n"
    
    for line in lines:
        for i, col in enumerate(line.values()):
            ret_str += f"{col:^{col_widths[i]}}"
        ret_str += "\n"
    return ret_str

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
Hello,
A new invoice has been created by {invoice['creator']} and is awaiting approval from an authorized user.

Invoice Details:
Record ID: {invoice_id}
Total Lines: {len(invoice['li'])}
Created By: {invoice['creator']}
Created On: {invoice['date']}
Invoice Address:
{address}

Line Details:
{lines}

Taxes: ${invoice['tax']}
Fees: ${invoice['fees']}
Total: ${invoice['total']}

A officer docket item has been generated to review this invoice.

This is an automated email sent from an unmonitored inbox. If you have any questions, please reach out to csclub@bridgew.edu.
    """
    email_recip = db.get_approver_emails()
    db.close()
    
    
    send_email(subject, message_body, 
              "cclub9516@gmail.com", email_recip,
              [], [], email_settings["smtp_host"], email_settings['username'],
              email_settings['password'], use_ssl=True)
    
def alert_users_of_updated_invoice(invoice_id):
    db = connect(**db_settings)
    invoice = db.get_invoice_by_id(invoice_id)
    subject = f"New Financial Record: {invoice['type']} #{invoice_id}"
    address = '\n'.join(invoice['return_addr'])
    lines = format_lines(invoice['li'])
    
    message_body = f"""
Hello,
An invoice has been updated! The original invoice was created by {invoice['creator']} and is awaiting approval from an authorized user.

Invoice Details:
Record ID: {invoice_id}
Total Lines: {len(invoice['li'])}
Created By: {invoice['creator']}
Created On: {invoice['date']}
Invoice Address:
{address}

Line Details:
{lines}

Taxes: ${invoice['tax']}
Fees: ${invoice['fees']}
Total: ${invoice['total']}

A officer docket item has been generated to review this invoice.

This is an automated email sent from an unmonitored inbox. If you have any questions, please reach out to csclub@bridgew.edu.
    """
    email_recip = db.get_approver_emails()
    db.close()
    
    
    send_email(subject, message_body, 
              "cclub9516@gmail.com", email_recip,
              [], [], email_settings["smtp_host"], email_settings['username'],
              email_settings['password'], use_ssl=True)
    
def alert_invoice_new(invoice_id):
    # convert_url_to_pdf(f'https://officers.compscibridgew.info/invoices/view/{invoice_id}', f'Invoice{invoice_id}.pdf')
    alert_users_of_new_invoice(invoice_id)
    create_docket_item(invoice_id)
    
    
def alert_invoice_update(invoice_id):
    # convert_url_to_pdf(f'https://officers.compscibridgew.info/invoices/view/{invoice_id}', f'Invoice{invoice_id}.pdf')
    alert_users_of_updated_invoice(invoice_id)
    create_docket_item(invoice_id)