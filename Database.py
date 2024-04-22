import sqlite3

class SQLink:
    def __init__(self, dbname):
        self.db = sqlite3.connect(dbname)
        self.cursor = self.db.cursor()

    def Set_Columns_To(self, columns):
        self.columns = columns

    def Set_Table_To(self, tablename):
        self.tablename = tablename
        self.cursor.execute(f'PRAGMA table_info({self.tablename})')
        rows = self.cursor.fetchall()

        if len(rows) == 0 or len(rows) != len(self.columns):
            return False

        for x in range(len(rows)):
            if rows[x][1] != self.columns[x][0]:
                return False
 
        return True

    def Create_Table(self):
        columns_str = ', '.join([f'{name} {type}' for name, type in self.columns])

        self.cursor.execute(f'DROP TABLE IF EXISTS {self.tablename}')

        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {self.tablename}  ({columns_str})''')

        self.db.commit()

    def Add_Data(self, data):

        cols = ', '.join([x[0] for x in data])

        marks = ', '.join(['?' for _ in data])

        self.cursor.execute(f'''INSERT INTO {self.tablename} ({cols}) VALUES ({marks})''', 
            ([x[1] for x in data]))

        self.db.commit()

    def Get_Data_By_Column(self, column_name, value):
        self.cursor.execute(f'''SELECT * FROM {self.tablename} WHERE {column_name} = ?''', (value,))
        rows =  self.cursor.fetchall()
        return rows

    def Del_Data_By_Column(self, column_name, value):
        self.cursor.execute(f'''DELETE FROM {self.tablename} WHERE {column_name} = ?''', (value,))
        self.db.commit()

    def Get_All_Data(self):
        self.cursor.execute(f'''SELECT * FROM {self.tablename}''')
        rows =  self.cursor.fetchall()
        return rows