import mysql.connector
from typing import List, Dict, NoReturn
import datetime
import utils.app_utils as app_utils

class connect:
    def __init__(self, host, user, passwd, db):
        self.db = mysql.connector.connect(
            host=host,
            user=user,
            passwd=passwd,
            database=db
        )
        self.cursor = self.db.cursor(buffered=True)
    
    def get_records(self) -> List:
        return_list = []
        invoice_sql = """
        select a.invoiceID, a.createdDate, b.user_full_name, c.user_full_name, d.recordName, e.line1, e.line2, e.line3, e.line4, a.tax, a.fees, a.total, f.statusDesc
from invoice a, allowedusers b, allowedusers c, recordtype d, addresses e, statuses f
where a.creator = b.userSeq and a.approved_by = c.userSeq and a.recordType = d.typeSeq and a.return_addr =
e.addrSeq and a.statusID = f.statusID;
        """
        line_sql = """
        SELECT lineID, `desc`, unit_price, qty, total FROM line WHERE invoiceID = %s
        """
        self.cursor.execute(invoice_sql)
        invoices = self.cursor.fetchall()
        for invoice in invoices:
            self.cursor.execute(line_sql, (invoice[0],))
            lines = self.cursor.fetchall()
            return_list.append(
                {
                    "id": str(invoice[0]),
                    "date": invoice[1],
                    "creator": invoice[2],
                    "approver": invoice[3],
                    "type": invoice[4],
                    "tax": invoice[9],
                    "fees": invoice[10],
                    "total": invoice[11],
                    "status": invoice[12],
                    "li": [
                        {
                            "line": line[0],
                            "desc": line[1],
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
                }
            )
        return return_list
    
    def get_user_name(self, id: str) -> str:
        user = self.get_user_by_id(id)
        return user[1]
    
    def get_user_by_id(self, id: str) -> list:
        sql = "SELECT userID, user_full_name, userSeq, emailAddr FROM allowedUsers where userID = %s"
        self.cursor.execute(sql, (id,))
        user_data = self.cursor.fetchone()
        #print(user_data)
        return user_data
    
    def create_user(self, user_data: Dict) -> int:
        sql = """INSERT INTO allowedUsers (userID, user_full_name, emailAddr) VALUES (%s, %s, %s)"""
        vals = (user_data.get("UserID"),
                user_data.get("userName"),
                user_data.get("emailID"))
        self.cursor.execute(sql, vals)
        self.db.commit()
        return self.cursor.lastrowid
    
    def get_users(self) -> List:
        sql = "SELECT * FROM allowedUsers"
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    
    def create_user_perms(self, userSeq, perms: dict):
        sql = """
        INSERT INTO permissions
        (userSeq, invEdit, invView, docEdit, docView, invAdmin, docAdmin,
        canApproveInvoices, canReceiveEmails, userAdmin) VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        vals = (
            userSeq,
            perms.get("EI") == "on",
            perms.get("RI") == "on",
            perms.get("ED") == "on",
            perms.get("RD") == "on",
            perms.get("AI") == "on",
            perms.get("AD") == "on",
            perms.get("AP") == "on",
            perms.get("RE") == "on",
            perms.get("UA") == "on"
        )
        self.cursor.execute(sql, vals)
        self.db.commit()
    
    def get_all_user_perms(self) -> List:
        sql = """
        SELECT a.user_full_name, a.emailAddr, b.invView, b.invEdit, b.invAdmin, b.docView, b.docEdit,
        b.docAdmin, b.userAdmin, b.canApproveInvoices, 
        b.canReceiveEmails from allowedUsers a, permissions b where
        a.userSeq = b.userSeq and a.user_full_name != '' and a.user_full_name 
        not like 'SGA%';
        """
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    
    def get_all_user_info(self, userSeq):
        sql = """SELECT a.user_full_name, a.userID, a.emailAddr,
        b.invEdit, b.invView, b.docEdit, b.docView, b.invAdmin,
        b.docAdmin, b.canApproveInvoices, b.userAdmin,
        b.canReceiveEmails, a.theme from allowedUsers a, permissions b where
        a.userSeq = b.userSeq and a.userSeq = %s;"""
        self.cursor.execute(sql, (userSeq,))
        return self.cursor.fetchone()
    
    def get_user_full(self, seq: str) -> list[str]:
        sql = "SELECT userID, user_full_name, userSeq FROM allowedUsers where userSeq = %s"
        self.cursor.execute(sql, (seq,))
        user_data = self.cursor.fetchone()
        return user_data
    
    def get_user_id(self, userSeq: int):
        user_sql = """SELECT userID from allowedusers where userSeq = %s"""
        self.cursor.execute(user_sql, (userSeq,))
        return str(self.cursor.fetchone()[0])
    
    def get_user_permissions(self, userID: str) -> list[bool]:
        user_info = self.get_user_by_id(userID)
        if user_info is None:
            raise app_utils.UserAccessNotSignedInException
        userSeq = user_info[2]
        perm_sql = "SELECT invEdit, invView, docEdit, docView, invAdmin, docAdmin, canApproveInvoices, userAdmin from permissions where userSeq = %s"
        self.cursor.execute(perm_sql, (userSeq,))
        return self.cursor.fetchone()
    
    def can_user_edit_invoice(self, userID) -> bool | NoReturn:
        user_perms = self.get_user_permissions(userID)
        if user_perms[0] != 1 and user_perms[4] != 1:
            raise app_utils.UserAccessInvoiceNoEditException
        return True
    
    def can_user_view_invoice(self, userID) -> bool | NoReturn:
        user_perms = self.get_user_permissions(userID)
        if user_perms[1] != 1 and user_perms[4] != 1:
            raise app_utils.UserAccessInvoiceNoReadException
        return True
    
    def can_user_edit_docket(self, userID) -> bool | NoReturn:
        user_perms = self.get_user_permissions(userID)
        if user_perms[2] != 1 and user_perms[5] != 1:
            raise app_utils.UserAccessDocketNoEditException
        return True
    
    def can_user_view_docket(self, userID) -> bool | NoReturn:
        user_perms = self.get_user_permissions(userID)
        if user_perms[3] != 1 and user_perms[5] != 1:
            raise app_utils.UserAccessDocketNoReadException
        return True
    
    def is_user_invoice_admin(self, userID) -> bool | NoReturn:
        user_perms = self.get_user_permissions(userID)
        if user_perms[4] != 1:
            raise app_utils.UserAccessInvoiceNoAdminException
        return True
    
    def is_user_admin(self, userID) -> bool | NoReturn:
        user_perms = self.get_user_permissions(userID)
        if user_perms[7] != 1:
            raise app_utils.UserAccessNoAdminException
        return True
    
    def is_user_docket_admin(self, userID) -> bool | NoReturn:
        user_perms = self.get_user_permissions(userID)
        if user_perms[5] != 1:
            raise app_utils.UserAccessDocketNoAdminException
        return True
    
    def is_user_app_admin(self, userID) -> bool | NoReturn:
        user_perms = self.get_user_permissions(userID)
        if user_perms[7] != 1:
            raise app_utils.UserAccessDocketNoAdminException
        return True
    
    def can_user_approve_invoice(self, userID) -> bool | NoReturn:
        user_perms = self.get_user_permissions(userID)
        if (user_perms[6] != 1) and (not user_perms[4]):
            raise app_utils.UserAccessInvoiceNoApproveException
        return True
    
    def get_user_color_theme(self, userID) -> int:
        sql = """
        SELECT theme FROM allowedUsers where userID = %s"""
        self.cursor.execute(sql, (userID,))
        return self.cursor.fetchone()

    def validate_address(self, address: List[str], addr_desc: str) -> int:
        self.cursor.execute("SELECT * FROM addresses")
        myresult = self.cursor.fetchall()
        for x in myresult:
            if all([a == b for a, b in zip(address, x[1:])]) \
                    and addr_desc == x[5]:
                return x[0]
        # Address not found. Add it to the database
        return self.create_address(address, addr_desc)
    
    def is_user_valid(self, userID: str) -> NoReturn | None:
        if userID is None:
            raise app_utils.UserAccessNotSignedInException
        users = self.get_available_users()
        if userID not in users:
            raise app_utils.UserAccessNotSignedInException
        
    def create_address(self, address: List[str], addr_desc: str) -> int:
        sql = """INSERT INTO addresses (Line1, Line2, Line3, Line4, addrName)
                 VALUES (%s, %s, %s, %s, %s)"""
        val = tuple(address) + (addr_desc,)
        self.cursor.execute(sql, val)
        self.db.commit()
        return self.cursor.lastrowid
    
    def get_next_invoice_id(self):
        sql = "SELECT * FROM invoice"
        self.cursor.execute(sql)
        myresult = self.cursor.fetchall()
        used_ids = [x[0] for x in myresult]
        if len(used_ids) == 0: return 1
        max_result = max(used_ids)
        i = 1
        while i <= max_result:
            if i not in used_ids:
                break
            i += 1
        return i
    
    def validate_status(self, status: str) -> int:
        sql = """SELECT * FROM statuses"""
        self.cursor.execute(sql)
        valid_statuses = self.cursor.fetchall()
        for valid_status in valid_statuses:
            if valid_status[1] == status:
                return valid_status[0]
        return self.create_status(status)

    def create_status(self, status: str) -> int:
        sql = """INSERT INTO statuses (statusDesc) VALUES (%s)"""
        self.cursor.execute(sql, (status,))
        self.db.commit()
        return self.cursor.lastrowid
    
    def create_invoice(self, id: int, creator: str, approver: str,
                       type: str, return_addr: List[str], tax: float,
                       fees: int, total: float, status: str, date: str,
                       li: list, addr_desc: str) -> int:
        creator_userSeq = self.get_user_seq(creator)
        approver_userSeq = self.get_user_seq(approver)
        
        creator_userID = self.get_user_id(creator_userSeq)
        approver_userID = self.get_user_id(approver_userSeq)
        
        print(creator)
        if(not self.can_user_edit_invoice(creator_userID)):
            return -1
        if(not self.can_user_approve_invoice(approver_userID)):
            return -1  
        addr_id = self.validate_address(return_addr, addr_desc)
        status_id = self.validate_status(status)
        creator = creator_userSeq
        typeID = self.get_type_id(type)
        approver = approver_userSeq
        val = (id, getDateObj(date), creator, approver, typeID, addr_id,
               tax, fees, total, status_id)
        sql = """
        INSERT INTO invoice (invoiceID, createdDate, creator, approved_by,
        recordType, return_addr, tax, fees, total, statusID) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        self.cursor.execute(sql, val)
        self.db.commit()
        
        lineIDs: List[int] = []
        for line in li:
            lineIDs.append(self.create_line(id, line))
        
        return [id, lineIDs, approver == 0]
        
    def create_line(self, invoiceID, line: Dict) -> int:
        sql = """
        INSERT INTO line (invoiceID, lineID, `desc`, unit_price, qty, total)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (invoiceID, line.get("line"), line.get("desc"), line.get("ammt"), line.get("qty"), line.get("total"))
        self.cursor.execute(sql, values)
        self.db.commit()
        return self.cursor.lastrowid
        
    def get_user_seq(self, user_name: str) -> int:
        sql = "select userSeq from allowedusers where user_full_name = %s"
        self.cursor.execute(sql, (user_name,))
        return int(self.cursor.fetchone()[0])
    
    def get_type_id(self, typeDesc: str) -> int:
        sql = """SELECT * FROM recordtype"""
        self.cursor.execute(sql)
        valid_statuses = self.cursor.fetchall()
        for valid_status in valid_statuses:
            if valid_status[1] == typeDesc:
                return valid_status[0]
        return self.create_type(typeDesc)
    
    
    def create_type(self, typeDesc: str) -> int:
        sql = """INSERT INTO recordtype (recordName) VALUES (%s)"""
        self.cursor.execute(sql, (typeDesc,))
        self.db.commit()
        return self.cursor.lastrowid
    
    def update_record(self, id: int, approver: str,
                       type: str, return_addr: List[str], tax: float,
                       fees: int, total: float, status: str, date: str,
                       li: list, addr_desc: str, creator: str):
        approver = self.get_user_seq(approver)
        if(not self.can_user_approve_invoice(approver)):
            return -1
        addr_id = self.validate_address(return_addr, addr_desc)
        status_id = self.validate_status(status)
        typeID = self.get_type_id(type)
        
        val = (getDateObj(date), approver, typeID, addr_id,
               tax, fees, total, status_id, id)
        sql = """
        UPDATE invoice SET createdDate = %s, approved_by = %s,
        recordType = %s, return_addr = %s, tax = %s, fees = %s, total = %s,
        statusID = %s WHERE invoiceID = %s
        """
        self.cursor.execute(sql, val)
        self.db.commit()
        for line in li:
            self.update_line(id, line)
        if approver == 0:
            return 1 # Invoice isn't approved yet. Send an email to all Approvers
        
    def update_line(self, invoiceID: int, line: Dict):
        sql = """
        UPDATE line SET `desc` = %s, unit_price = %s, qty = %s, total = %s
        WHERE invoiceID = %s AND lineID = %s
        """
        # Before we update, check if the line exists
        sql_check = """
        SELECT * FROM line WHERE invoiceID = %s AND lineID = %s
        """
        val_check = (invoiceID, line.get("line"))
        self.cursor.execute(sql_check, val_check)
        if self.cursor.rowcount == 0:
            self.create_line(invoiceID, line)
            return
        values = (line.get("desc"), line.get("ammt"), line.get("qty"), line.get("total"), invoiceID, line.get("line"))
        self.cursor.execute(sql, values)
        self.db.commit()
            
    def get_available_users(self) -> List[str]:
        sql = "SELECT userID FROM allowedUsers"
        self.cursor.execute(sql)
        myresult = self.cursor.fetchall()
        return [x[0] for x in myresult]
    
    def close(self):
        self.db.commit()
        self.db.close()
        
    def get_available_statuses(self) -> List[str]:
        sql = "SELECT statusDesc FROM statuses"
        self.cursor.execute(sql)
        myresult = self.cursor.fetchall()
        return [x[0] for x in myresult]
    
    def get_available_types(self) -> List[str]:
        sql = "SELECT recordName FROM recordtype"
        self.cursor.execute(sql)
        myresult = self.cursor.fetchall()
        return [x[0] for x in myresult]
    
    def update_type_info(self, id, desc):
        sql = "UPDATE recordtype SET recordName = %s WHERE typeSeq = %s"
        self.cursor.execute(sql, (desc, id,))
        self.db.commit()
    
    def get_all_type_info(self) -> list[str]:
        sql = "SELECT typeSeq, recordName from recordtype"
        self.cursor.execute(sql)
        return self.cursor.fetchall()
        
    def get_available_addresses(self) -> List[str]:
        sql = "SELECT addrSeq, line1, line2, line3, line4, addrName FROM addresses"
        self.cursor.execute(sql)
        myresult = self.cursor.fetchall()
        return myresult
    
    def get_address_by_seq(self, addrSeq):
        sql = "SELECT addrSeq, line1, line2, line3, line4, addrName FROM addresses WHERE addrSeq = %s"
        self.cursor.execute(sql, (addrSeq,))
        return self.cursor.fetchall()[0]
        
    def get_invoice_by_id(self, invoice_id: int):
        invoice_sql = """
        select a.invoiceID, a.createdDate, b.user_full_name, c.user_full_name, d.recordName, e.line1, e.line2, e.line3, e.line4, a.tax, a.fees, a.total, f.statusDesc
from invoice a, allowedusers b, allowedusers c, recordtype d, addresses e, statuses f
where a.creator = b.userSeq and a.approved_by = c.userSeq and a.recordType = d.typeSeq and a.return_addr =
e.addrSeq and a.statusID = f.statusID and a.invoiceID = %s;
        """
        line_sql = """
        SELECT lineID, `desc`, unit_price, qty, total FROM line WHERE invoiceID = %s
        """
        self.cursor.execute(invoice_sql, (invoice_id,))
        invoice = self.cursor.fetchone()
        self.cursor.execute(line_sql, (invoice[0],))
        lines = self.cursor.fetchall()
        invoice_data = {
                "id": str(invoice[0]),
                "date": invoice[1],
                "creator": invoice[2],
                "approver": invoice[3],
                "type": invoice[4],
                "tax": invoice[9],
                "fees": invoice[10],
                "total": invoice[11],
                "status": invoice[12],
                "li": [
                    {
                        "line": line[0],
                        "desc": line[1],
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
            }
        return invoice_data

    def get_approver_emails(self) -> list[str]:
        sql = "SELECT a.emailAddr FROM allowedusers a, permissions b where a.userSeq = b.userSeq and b.canReceiveEmails = 1 and b.canApproveInvoices = 1 AND a.isSystemUser = 0"
        self.cursor.execute(sql)
        myresult = self.cursor.fetchall()
        return [x[0] for x in myresult]
    
    def get_status_info(self):
        sql = "SELECT * FROM statuses"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def update_user_info(self, user_seq, user_info):
        sql = """
        UPDATE allowedUsers SET
        userID = %s,
        user_full_name = %s,
        emailAddr = %s,
        theme = %s
        WHERE userSeq = %s
        """
        vals = (
            user_info["UserID"],
            user_info["userName"],
            user_info["emailID"],
            user_info["theme"],
            user_seq
        )
        self.cursor.execute(sql, vals)
        self.db.commit()
        
    def update_status_info(self, status_seq, status_info):
        sql = """
        UPDATE statuses SET
        statusDesc = %s
        WHERE statusID = %s
        """
        vals = (
            status_info,
            status_seq
        )
        self.cursor.execute(sql, vals)
        self.db.commit()
    
    def update_address(self, addr_seq, addr_data):
        sql = """
        UPDATE addresses
        SET line1 = %s,
        line2 = %s,
        line3 = %s,
        line4 = %s,
        addrName = %s
        WHERE addrSeq = %s
        """
        vals = (
            addr_data['line1'],
            addr_data['line2'],
            addr_data['line3'],
            addr_data['line4'],
            addr_data['desc'],
            addr_seq
        )
        
        self.cursor.execute(sql, vals)
        self.db.commit()
        
    def update_user_perms(self, user_seq, perms):
        sql = """
        UPDATE permissions SET
        invEdit = %s,
        invView = %s,
        docEdit = %s,
        docView = %s,
        invAdmin = %s,
        docAdmin = %s,
        canApproveInvoices = %s,
        canReceiveEmails = %s,
        userAdmin = %s
        WHERE userSeq = %s
        """
        vals = (
            perms.get("EI") == "on",
            perms.get("RI") == "on",
            perms.get("ED") == "on",
            perms.get("RD") == "on",
            perms.get("AI") == "on",
            perms.get("AD") == "on",
            perms.get("AP") == "on",
            perms.get("RE") == "on",
            perms.get("UA") == "on",
            user_seq
        )
        self.cursor.execute(sql, vals)
        self.db.commit()

def format_date(date: datetime.datetime) -> str:
    return date.strftime("%d %b, %Y")


def getDateObj(date: str) -> datetime.datetime:
    date_split = date.split()
    day = int(date_split[0])+1
    month = date_split[1][:-1]
    year = int(date_split[2])
    month_dict = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12
    }
    return datetime.datetime(year, month_dict[month], day, 0, 0, 0)
