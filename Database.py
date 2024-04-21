import sqlite3

class SQLink:
    def __init__(self, dbname):
        self.db = sqlite3.connect(dbname)
        self.cursor = self.db.cursor()

    def Set_Columns_To(self, columns):
        self.columns = columns

    def Set_Table_To(self, tablename):
        self.tablename = tablename
        self.cursor.execute(f"PRAGMA table_info({self.tablename})")
        rows = self.cursor.fetchall()

        if len(rows) == 0:
            return False

        for x in range(len(rows)):
            if rows[x][1] != self.columns[x][0]:
                return False
 
        return True

    def Create_Table(self):
        columns_str = ', '.join([f'{name} {type}' for name, type in self.columns])

        self.cursor.execute(f"DROP TABLE IF EXISTS {self.tablename}")

        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {self.tablename}  ({columns_str})''')

        print(f'''CREATE TABLE IF NOT EXISTS {self.tablename}  ({columns_str})''')

        self.db.commit()

    def Add_Data(self, data):
        self.cursor.execute(f'''INSERT INTO {self.tablename} ({data[0][0]}, {data[1][0]}, {data[2][0]}, {data[3][0]}) VALUES (?, ?, ?, ?)''', 
               (data[0][1], data[1][1], data[2][1], data[3][1]))

        self.db.commit()

    def Get_Data(self):
        self.cursor.execute(f'''SELECT * FROM {self.tablename} LIMIT 5''')

        rows = self.cursor.fetchall()

        return rows