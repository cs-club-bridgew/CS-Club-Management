import mysql.connector
from typing import List
import datetime


class connect:
    def __init__(self, host, user, passwd, db):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db
        self.mydb = mysql.connector.connect(
            host=self.host,
            user=self.user,
            passwd=self.passwd,
            database=self.db
        )
        self.mycursor = self.mydb.cursor()

    def validate_address(self, address: List[str], addr_desc: str) -> int:
        self.mycursor.execute("SELECT * FROM addresses")
        myresult = self.mycursor.fetchall()
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
        self.mycursor.execute(sql, val)
        self.mydb.commit()
        return self.mycursor.lastrowid

    def create_record(self, id: int, creator: str,
                      approver: str, type: str,
                      return_addr: List[str],
                      tax: float | int, fees: float | int,
                      status: str, total: float | int, date: str, li: List,
                      addr_desc: str) -> int:
        sql = """
        insert into record (id, createdDate, creator, approver,
        recordType, return_addr, tax, fees, total, statusID)
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        addr_id = self.validate_address(return_addr, addr_desc)
        status_id = self.get_status_id(status)
        val = (id, getDateObj(date), creator, approver, type, addr_id,
               tax, fees, total, status_id)
        self.mycursor.execute(sql, val)
        self.mydb.commit()
        return self.mycursor.lastrowid

    def create_item(self, record_id, **line_data) -> int:
        # Get the current list of items
        self.mycursor.execute("SELECT * FROM inv_line" +
                              f" WHERE recordID = {record_id}")
        myresult = self.mycursor.fetchall()
        if line_data.get("line") is None:
            # Get the next id
            if len(myresult) == 0:
                line_data['line'] = 1
            else:
                line_data['line'] = max([x[0] for x in myresult]) + 1
        sql = """INSERT INTO inv_line
        (recordID, line, `desc`, ammt, qty, total) VALUES
        (%s, %s, %s, %s, %s, %s)"""
        ammt = float(line_data.get("ammt", 0))
        qty = float(line_data.get("qty", 0))
        val = (record_id, line_data['line'], line_data.get("desc"), ammt, qty,
               ammt * qty)
        self.mycursor.execute(sql, val)
        self.mydb.commit()
        return self.mycursor.lastrowid

    def update_record(self, **data) -> int:
        sql = "UPDATE record SET "
        params = []
        for key, value in data.items():
            if key == "return_addr":
                addr_name = data.get("addr_desc", "")
                value = self.validate_address(value, addr_name)
            if key == "total":
                status = self.get_status_id(data.get("status"))
                if status == 6:
                    value = 0
            if key == "status":
                key = 'statusID'
                value = self.get_status_id(value)
                if value == 6:

                    data['total'] = 0
            if key in ["creator", 'li', 'id', 'addr_desc']:
                continue
            if key == "date":
                key = "createdDate"
                value = getDateObj(value)
            if key == "type":
                key = "recordType"
            params.append(f"`{key}` = '{value}'")
        sql += ", ".join(params)
        sql += f" WHERE id = {data.get('id')}"
        self.mycursor.execute(sql)

    def get_status_id(self, status: str) -> int:
        self.mycursor.execute("SELECT * FROM statuses WHERE statusDesc = " +
                              f"'{status}'")
        myresult = self.mycursor.fetchall()
        if len(myresult) == 0:
            raise Exception(f"Status {status} not found.")
        return myresult[0][0]

    def get_status(self, status_id: int) -> str:
        self.mycursor.execute("SELECT * FROM statuses WHERE statusID = " +
                              f"{status_id}")
        myresult = self.mycursor.fetchall()
        return myresult[0][1]

    def get_next_invoice_id(self) -> int:
        sql = "SELECT * FROM record"
        self.mycursor.execute(sql)
        myresult = self.mycursor.fetchall()
        used_ids = [x[0] for x in myresult]
        max_result = max(used_ids)
        i = 1
        while i <= max_result:
            if i not in used_ids:
                break
            i += 1
        return i

    def get_records(self) -> List:
        record_sql = """
        SELECT a.id, a.createdDate, a.creator, a.approver, a.recordType, a.tax,
        a.fees, a.total, a.return_addr, b.statusDesc FROM record a, statuses b
        WHERE a.statusID = b.statusID
        """
        line_sql = """
        SELECT line, `desc`, ammt, qty, total FROM inv_line WHERE recordID = %s
        """
        self.mycursor.execute(record_sql)
        myresult = self.mycursor.fetchall()
        records = []
        for record in myresult:
            self.mycursor.execute(line_sql, (record[0],))
            lines = self.mycursor.fetchall()
            records.append({
                "id": str(record[0]),
                "date": format_date(record[1]),
                "creator": record[2],
                "approver": record[3],
                "type": record[4],
                "tax": record[5],
                "fees": record[6],
                "total": record[7],
                "status": record[9],
                "li": [],
                "return_addr": self.get_address(record[8])
                }
            )
            for x in lines:
                records[-1]["li"].append({
                    "line": x[0],
                    "desc": x[1],
                    "ammt": x[2],
                    "qty": x[3],
                    "total": x[4]
                })
        return records

    def get_record_by_id(self, id: int) -> dict:
        record_sql = """
        SELECT a.id, a.createdDate, a.creator, a.approver, a.recordType, a.tax,
        a.fees, a.total, a.return_addr, b.statusDesc FROM record a, statuses b
        WHERE a.statusID = b.statusID and a.id = %s
        """
        line_sql = """
        SELECT line, `desc`, ammt, qty, total FROM inv_line WHERE recordID = %s
        """
        values = (id,)
        self.mycursor.execute(record_sql, values)
        records = self.mycursor.fetchone()
        self.mycursor.execute(line_sql, values)
        lines = self.mycursor.fetchall()
        record = {
            "id": str(records[0]),
            "date": format_date(records[1]),
            "creator": records[2],
            "approver": records[3],
            "type": records[4],
            "tax": records[5],
            "fees": records[6],
            "total": records[7],
            "status": records[9],
            "li": [],
            "return_addr": self.get_address(records[8])
        }
        for x in lines:
            record["li"].append({
                "line": x[0],
                "desc": x[1],
                "ammt": x[2],
                "qty": x[3],
                "total": x[4]
            })
        return record

    def get_available_addresses(self):
        sql = "SELECT * FROM addresses"
        self.mycursor.execute(sql)
        myresult = self.mycursor.fetchall()
        return myresult

    def get_address(self, id: int) -> List[str]:
        if id is None:
            return ["", "", "", ""]
        self.mycursor.execute(f"SELECT Line1, Line2, Line3, Line4 FROM addresses WHERE addrSeq = {id}")
        myresult = self.mycursor.fetchall()
        return myresult[0]

    def update_line(self, recordID, lineNum, **data) -> int:
        sql = "SELECT * FROM inv_line WHERE recordID = %s"
        values = (recordID,)
        self.mycursor.execute(sql, values)
        myresult = self.mycursor.fetchall()
        if len(myresult) == 0:
            return self.create_item(recordID, **data)
        sql = "UPDATE inv_line SET "
        params = []
        for key, value in data.items():
            if key == "line":
                continue
            params.append(f"`{key}` = '{value}'")
        sql += ", ".join(params)
        sql += f" WHERE recordID = {recordID} AND line = {lineNum}"
        self.mycursor.execute(sql)
        self.mydb.commit()
        return self.mycursor.lastrowid

    def get_available_users(self) -> List[str]:
        sql = "SELECT * FROM allowedUsers"
        self.mycursor.execute(sql)
        myresult = self.mycursor.fetchall()
        return [x[0] for x in myresult]

    def close(self):
        self.mydb.commit()
        self.mydb.close()
        


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
