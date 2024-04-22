from fastapi import FastAPI, HTTPException
from datetime import datetime

from Sensor import SensorData, SensorState
from Blocks import BlockID
from Database import SQLink

app = FastAPI()

# Create SQL instance for saving sensor readings
sql = SQLink('SensorDB.db')

cols = [('sensor_id', 'text'), 
        ('time', 'text'), 
        ('temperature', 'real')]

sql.Set_Columns_To(cols)

# if Given table does not match given columns create new table
if sql.Set_Table_To('readings') is False:
    sql.Create_Table()


# Create SQL instance for block-sensor_id links
sql2 = SQLink('SensorDB.db')

cols2 = [('block_id', 'text'),
        ('sensor_id', 'text'),
        ('sensor_state', 'boolean')]

sql2.Set_Columns_To(cols2)

# if Given table does not match given columns create new table
if sql2.Set_Table_To('blocks') is False:
    sql2.Create_Table()



# Add data to system
@app.post("/add/data")
async def sensor_data(input: SensorData):
    sql.Add_Data([('sensor_id', input.sensor_id), 
                ('time', datetime.now().strftime("%Y-%m-%d %H:%M:%S")), 
                ('temperature', input.temperature)])
    return {"details": "successful"}

# Add sensor to system
@app.post("/add/sensor")
async def sensor_add(input: BlockID):
    sql2.Del_Data_By_Column('sensor_id', input.sensor_id)
    sql2.Add_Data([('block_id', input.block_id), 
                ('sensor_id', input.sensor_id),
                ('sensor_state', True)])    
    return {"details": "successful"}
     

# Set state for sensor about error
@app.post("/state/error")
async def sensor_state(input: SensorState):
    rows = sql2.Get_Data_By_Column('sensor_id', input.sensor_id)
    if len(rows) < 1:
        raise HTTPException(status_code=404, detail="sensor not in system")
    sql2.Del_Data_By_Column('sensor_id', input.sensor_id)
    sql2.Add_Data([('block_id', rows[0][0]), 
                ('sensor_id', rows[0][1]),
                ('sensor_state', False)])   
    return {'detail': 'successful'}

# return sensor status
@app.get("/state/sensor/{sensor_id}")
async def sensor_state(sensor_id: str):
    rows = sql2.Get_Data_By_Column('sensor_id', sensor_id)
    if len(rows) < 1:
        raise HTTPException(status_code=404, detail="sensor not in system")
    return {'state': rows[0][2]}

