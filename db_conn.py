import sqlite3

class DBConn:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        
    def exec_query(self, query):
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.ProgrammingError:
            return None
    
    def create_table(self, table_name, columns):
        self.exec_query(f"CREATE TABLE {table_name} ({columns})")
    
    def insert(self, table_name, **values):
        columns = ", ".join(values.keys())
        values = ", ".join([f"'{value}'" for value in values.values()])
        self.exec_query(f"INSERT INTO {table_name} ({columns}) VALUES ({values})")