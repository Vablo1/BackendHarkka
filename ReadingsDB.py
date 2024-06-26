import sqlite3

Filename = 'SensorDB.db'

Columns = [('id', 'INTEGER PRIMARY KEY'), ('sensor_id', 'text'), ('time', 'text'), ('temperature', 'real')]

Table = 'readings'


class DataSQL:
    myinstance = None

    @classmethod
    def get_instance(cls):
        if cls.myinstance is None:
            cls.myinstance = DataSQL()
        return cls.myinstance

    def __init__(self):
        self.db = sqlite3.connect(Filename)
        self.cursor = self.db.cursor()

        self.cursor.execute(f'PRAGMA table_info({Table})')
        Real_Cols = self.cursor.fetchall()

        recreate_table = False

        if len(Real_Cols) == len(Columns):
            for n, col in enumerate(Real_Cols):
                if col[1] != Columns[n][0]:
                    recreate_table = True
        else:
            recreate_table = True

        if recreate_table:
            col_str = ', '.join([f'{name} {type}' for name, type in Columns])
            self.cursor.execute(f'''DROP TABLE IF EXISTS {Table}''')
            self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {Table}  ({col_str})''')
            self.db.commit()

    def Add_Data(self, data):

        cols = ', '.join([x[0] for x in data])

        marks = ', '.join(['?' for _ in data])

        self.cursor.execute(f'''INSERT INTO {Table} ({cols}) VALUES ({marks})''', 
            ([x[1] for x in data]))

        self.db.commit()

    def Get_Data_By_Column(self, column_name, value, orderby='', limit=0):

        query = f'''SELECT * FROM {Table} WHERE {column_name} = ?'''
        
        if orderby != '':
            query += f''' ORDER BY {orderby} DESC'''

        if limit != 0:
            query += f''' LIMIT {limit}'''

        query += ';'

        self.cursor.execute(query, (value,))

        rows =  self.cursor.fetchall()

        return [{name[0]: x[n] for n, name in enumerate(Columns)} for x in rows] 

    def Del_Data_By_Column(self, column_name, value):
        self.cursor.execute(f'''DELETE FROM {Table} WHERE {column_name} = ?''', (value,))
        self.db.commit()

    def Del_Data_By_Id(self, id):
        self.cursor.execute(f'''DELETE FROM {Table} WHERE id = ?''', (id,))
        self.db.commit()
        self.cursor.execute(search)
        return self.cursor.fetchall()

    def Get_Data_Between(self, sensor_id , time1, time2):

        if time1 < time2:
            start, end = time1, time2
        else:
            end, start = time1, time2

        self.cursor.execute(f'''SELECT * FROM {Table} WHERE time >= ? AND time <= ? AND sensor_id == ?''', (start, end, sensor_id))

        rows =  self.cursor.fetchall()

        return [{name[0]: x[n] for n, name in enumerate(Columns)} for x in rows] 

    def Get_Latest_Temp(self, sensor_id):
        self.cursor.execute(f'''SELECT * FROM {Table}
                                WHERE sensor_id is ?
                                ORDER BY time DESC
                                LIMIT 1''', (sensor_id,))
        rows = self.cursor.fetchall()
        return [{name[0]: x[n] for n, name in enumerate(Columns)} for x in rows] 




    # rows = sql.Get_Custom_Data(f'''SELECT sensor_id, time, temperature FROM {sql.tablename}
    #                                 WHERE sensor_id = '{sensor_id}' 
    #                                 AND time IN (
    #                                     SELECT min(time)
    #                                     FROM {sql.tablename}
    #                                     WHERE sensor_id = '{sensor_id}'
    #                                     GROUP BY strftime('%Y-%m-%dT%H', time)
    #                                 )
    #                                 ORDER BY time
    #                                 LIMIT 24;''')