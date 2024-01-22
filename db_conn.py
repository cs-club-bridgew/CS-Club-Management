import mysql.connector
from typing import List
import datetime

class connect:
    def __init__(self, host, user, passwd, db):
        self.db = mysql.connector.connect(
            host=host,
            user=user,
            passwd=passwd,
            database=db
        )
        self.cursor = self.db.cursor()
    
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
                        list(x) for x in lines
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
        user = self.get_user_full(id)
        return user[1]
    
    def get_user_full(self, id: str) -> list[str]:
        sql = "SELECT userID, user_full_name, userSeq FROM allowedUsers where userID = %s"
        self.cursor.execute(sql, (id,))
        user_data = self.cursor.fetchone()
        return user_data
    
    def get_user_permissions(self, userID: str) -> list[bool]:
        userSeq = self.get_user_full(userID)[2]
        perm_sql = "SELECT invEdit, invView, docEdit, docView, invAdmin, dockAdmin from permissions where userSeq = %s"
        self.cursor.execute(perm_sql, (userSeq,))
        return self.cursor.fetchone()
    
    def can_user_edit_invoice(self, userID) -> bool:
        user_perms = self.get_user_permissions(userID)
        return user_perms[0] == 1 or user_perms[4] == 1
    
    def can_user_view_invoice(self, userID) -> bool:
        user_perms = self.get_user_permissions(userID)
        return user_perms[1] == 1 or user_perms[4] == 1
    
    def can_user_edit_docket(self, userID) -> bool:
        user_perms = self.get_user_permissions(userID)
        return user_perms[2] == 1 or user_perms[5] == 1
    
    def can_user_view_docket(self, userID) -> bool:
        user_perms = self.get_user_permissions(userID)
        return user_perms[3] == 1 or user_perms[5] == 1
    
    def is_user_invoice_admin(self, userID) -> bool:
        user_perms = self.get_user_permissions(userID)
        return user_perms[4] == 1
    
    def is_user_docket_admin(self, userID) -> bool:
        user_perms = self.get_user_permissions(userID)
        return user_perms[5] == 1

    def validate_address(self, address: List[str], addr_desc: str) -> int:
        self.cursor.execute("SELECT * FROM addresses")
        myresult = self.cursor.fetchall()
        for x in myresult:
            if all([a == b for a, b in zip(address, x[1:])]) \
                    and addr_desc == x[5]:
                return x[0]
        # Address not found. Add it to the database
        return self.create_address(address, addr_desc)
    
    def create_address(self, address: List[str], addr_desc: str) -> int:
        sql = """INSERT INTO addresses (Line1, Line2, Line3, Line4, addrName)
                 VALUES (%s, %s, %s, %s, %s)"""
        val = tuple(address) + (addr_desc,)
        self.cursor.execute(sql, val)
        self.db.commit()
        return self.cursor.lastrowid
    
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
        addr_id = self.validate_address(return_addr, addr_desc)
        status_id = self.validate_status(status)
        creator = self.get_user_seq(creator)
        approver = self.get_user_seq(approver)
        val = (id, getDateObj(date), creator, approver, type, addr_id,
               tax, fees, total, status_id)
        sql = """
        INSERT INTO invoice VALUES
        (invoiceID, createdDate, creator, approved_by, 
        record_type, return_addr, tax, fees, total, statusID)"""
    
    def get_user_seq(self, user_name: str):
        sql = "select userSeq from allowedusers where user_full_name = %s"
        self.cursor.execute(sql, (user_name,))
        return self.cursor.fetchone()

def format_date(date: str) -> str:
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
