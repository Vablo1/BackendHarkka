from fastapi import FastAPI, HTTPException
from datetime import datetime

from Sensor import SensorData
from Blocks import BlockID
from Database import SQLink

app = FastAPI()

# Create SQL instance for saving sensor readings
sql = SQLink('SensorDB.db')

cols = [('sensor_id', 'text'), 
        ('time', 'text'), 
        ('temperature', 'real'), 
        ('error', 'boolean')]

sql.Set_Columns_To(cols)

# if Given table does not match given columns create new table
if sql.Set_Table_To('readings') is False:
    sql.Create_Table()


# Create SQL instance for block-sensor_id links
sql2 = SQLink('SensorDB.db')

cols2 = [('block_id', 'text'), 
        ('sensor_id', 'text')]

sql2.Set_Columns_To(cols2)

# if Given table does not match given columns create new table
if sql2.Set_Table_To('blocks') is False:
    sql2.Create_Table()



# Add data to system
@app.post("/add/data")
async def sensor_data(input: SensorData):
    sql.Add_Data([('sensor_id', input.sensor_id), 
                ('time', datetime.now().strftime("%Y-%m-%d %H:%M:%S")), 
                ('temperature', input.temperature), 
                ('error', input.error_state)])
    return {"details": "successful"}

# Add sensor to system
@app.post("/add/sensor")
async def sensor_add(input: BlockID):
    sql2.Add_Data([('block_id', input.block_id), 
                ('sensor_id', input.sensor_id)])    
    return {"details": "successful"}

