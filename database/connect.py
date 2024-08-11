import sqlite3
import configparser
config = configparser.ConfigParser()
config.read('database.ini')

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def __infer_type(self,value):
        try:
            if '.' in value:
                return float(value)
            elif "datetime" == value:
                return "datetime"
            else:
                return int(value)
        except ValueError:
            return value

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        self.tables_exist(conn)
        return conn

    def tables_exist(self, conn):
        cursor = conn.cursor()
        existing_tables = []
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for row in cursor.fetchall():
            existing_tables.append(row[0])
        for table in config.sections():
            if table not in existing_tables:
                self.create_tables(conn,table)

    def create_tables(self, conn,table):
        cursor = conn.cursor()
        sql = f"CREATE TABLE IF NOT EXISTS {table} (\n"
        column_defs = []
        
        for key, value in config.items(table):
            if key == "id":
                column_defs.append("id INTEGER PRIMARY KEY")
                continue
            typeValue = type(self.__infer_type(value))
            if typeValue == "datetime":
                column_defs.append(f"    {key} DATETIME NOT NULL")
            elif typeValue == str:
                column_defs.append(f"    {key} TEXT NOT NULL")
            elif typeValue == int:
                column_defs.append(f"    {key} INTEGER NOT NULL") 
            elif typeValue == float:
                column_defs.append(f"    {key} REAL NOT NULL") 
        sql += ",\n".join(column_defs)
        sql += "\n);"
        cursor.execute(sql)
        conn.commit()
        cursor.close()
