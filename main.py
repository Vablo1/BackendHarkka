from fastapi import FastAPI, HTTPException
from datetime import datetime

from Sensor import SensorData
from Database import SQLink

app = FastAPI()

# Create SQL instance for saving sensor readings
sql = SQLink('SensorDB.db')

cols = [('sensor_id', 'text'), 
        ('time', 'text'), 
        ('temperature', 'real'), 
        ('error', 'boolean')]

sql.Set_Columns_To(cols)

if sql.Set_Table_To('readings') is False:
    sql.Create_Table()


# Create SQL instance for block-sensor_id links
sql2 = SQLink('SensorDB.db')

cols2 = [('block_id', 'text'), 
        ('sensor_id', 'text')]

sql2.Set_Columns_To(cols)

if sql2.Set_Table_To('blocks') is False:
    sql2.Create_Table()




@app.post("/data")
async def sensor_data(input: SensorData):
    sql.Add_Data([('sensor_id', input.sensor_id), 
                ('time', datetime.now().strftime("%Y-%m-%d %H:%M:%S")), 
                ('temperature', input.temperature), 
                ('error', input.error_state)])

    for x in sql.Get_Data():
        print(x)

    return {"details": "successful"}

