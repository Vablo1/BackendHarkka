from fastapi import FastAPI, HTTPException
from datetime import datetime

from DataModels import *
from SensorsDB import BlockSQL
from ReadingsDB import DataSQL
from StatesDB import StateSQL

# uvicorn local:LocalApp --reload --port 8001

LocalApp = FastAPI(title='Local Sensor Management Backend',
                    description='Endpoints for adding measurements to backend',
                    version='V1.1')

@LocalApp.post('/add')
async def sensor_data(input: SensorData):

    DataSQL.get_instance().Add_Data([('sensor_id', input.sensor_id), 
                ('time', datetime.now().strftime('%Y-%m-%dT%H:%M:%S')), 
                ('temperature', input.temperature)])

    return {'details': 'successful'}


@LocalApp.post('/error')
async def sensor_data(input: SensorState):

    StateSQL.get_instance().Add_Data([('sensor_id', input.sensor_id), 
                ('time', datetime.now().strftime('%Y-%m-%dT%H:%M:%S')), 
                ('new_state', input.sensor_state)])

    return {'details': 'successful'}

@LocalApp.get('/check/{sensor_id}')
async def check_state(sensor_id: str):

    rows = StateSQL.get_instance().Get_Latest_state(sensor_id)

    if len(rows) < 1:

        check = BlockSQL.get_instance().Get_Data_By_Column('sensor_id', sensor_id)
        if len(check) < 1:
            raise HTTPException(status_code=404, detail='sensor not in system')

        return {'sensor_id': check[0].get('sensor_id'), 'state': 1}

    return {'sensor_id': sensor_id, 'state': rows[0].get('new_state')}
