from db_conn import connect
from db_config import db_settings

x = connect(**db_settings)

print(x.create_invoice(6, "Alex Dasneves", "", "Invoice", ["Test123","456","789","101112"], 0, 0, 0, 'Open', '23 Jan, 2024', [
    {
        "line": 1,
        "desc": "Test Item",
        "ammt": 0,
        "qty": 0,
        "total": 0
     }
    ], "Test Addr"
                 ))