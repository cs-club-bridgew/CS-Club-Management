from flask_liquid import render_template


if __name__ == "__main__":
    
    print(render_template("invoices/main.liquid", records=[{"id": 1, "type": "invoice", "status": "paid", "li": [{"item": "item1", "description": "desc1", "quantity": 1, "unit_price": 1, "total": 1}, {"item": "item2", "description": "desc2", "quantity": 2, "unit_price": 2, "total": 4}]}]))