from fastapi import FastAPI, HTTPException
from datetime import datetime

from DataModels import *
from SensorsDB import BlockSQL
from ReadingsDB import DataSQL
from StatesDB import StateSQL

# uvicorn remote:RemoteApp --reload --port 8000





RemoteApp = FastAPI(title='Sensor Management Backend',
                    description='Endpoints for getting measurements from backend',
                    version='V1.1')


@RemoteApp.put('/anturi', summary='Add sensor or change block')
async def sensor_add(input: BlockID):

    BlockSQL.get_instance().Del_Data_By_Column('sensor_id', input.sensor_id)
    BlockSQL.get_instance().Add_Data([('block_id', input.block_id), 
                ('sensor_id', input.sensor_id)])    

    return {'details': 'successful'}


@RemoteApp.post('/anturi')
async def set_sensor_state(input: SensorState):

    rows = BlockSQL.get_instance().Get_Data_By_Column('sensor_id', input.sensor_id)

    if len(rows) < 1:
        raise HTTPException(status_code=404, detail='sensor not in system')
    
    StateSQL.get_instance().Add_Data([('sensor_id', input.sensor_id), 
                ('time', datetime.now().strftime('%Y-%m-%dT%H:%M:%S')), 
                ('new_state', input.sensor_state)])

    return {'detail': 'successful'}


@RemoteApp.get('/anturit', summary='Listaa kaikki anturit (tunniste, lohko, tila).')
async def get_all_sensors():

    rows = BlockSQL.get_instance().Get_All_Data()

    output = []

    for x in rows:
        mydict = {'sensor_id': x.get('sensor_id'), 'block_id': x.get('block_id'), 'state': 1}

        state = StateSQL.get_instance().Get_Latest_state(x.get('sensor_id'))
        if len(state) > 0:
            mydict['state'] = state[0].get('new_state')

        output.append(mydict)

    return output



@RemoteApp.get('/anturit/{block_id}', summary='Listaa tietyn lohkon kaikki anturit (tunniste, tila, viimeisin mitta-arvo ja aikaleima)')
async def get_sensor_by_block(block_id: str):
    data = BlockSQL.get_instance().Get_Data_By_Column('block_id', block_id)

    if len(data) < 1:
        raise HTTPException(status_code=404, detail='no sensors in given block')

    statesql = StateSQL.get_instance()
    datasql = DataSQL.get_instance()

    output = []

    for x in data:

        current = {'sensor_id': x.get('sensor_id'), 'block_id': x.get('block_id')}

        state = statesql.Get_Latest_state(x.get('sensor_id'))
        temp = datasql.Get_Latest_Temp(x.get('sensor_id'))

        if len(state) > 0:
            current['state'] = state[0].get('new_state')
        else:
            current['state'] = 1

        if len(temp) > 0:
            current['data'] = {'timestamp': temp[0].get('time'), 'temperature': temp[0].get('temperature')}
        else:
            current['data'] = None

        output.append(current)

    return output


@RemoteApp.get('/anturi/{sensor_id}', summary='Näyttää yksittäisen anturin kaikki tiedot (tunniste, lohko, tila, mitta-arvot ajanhetkille')
async def get_sensor_state(sensor_id: str):

    sensor = BlockSQL.get_instance().Get_Data_By_Column('sensor_id', sensor_id)

    if len(sensor) < 1:
        raise HTTPException(status_code=404, detail='sensor not in system')

    rows = DataSQL.get_instance().Get_Data_By_Column('sensor_id', sensor_id, 'time', 10)

    values = [{'id': x.get('id'), 'timestamp': x.get('time'), 'temperature': x.get('temperature')} for x in rows]

    state = StateSQL.get_instance().Get_Latest_state(sensor[0].get('sensor_id'))

    if len(state) > 0:
        val_state = state[0].get('new_state')
    else:
        val_state = 1

    return {'block_id': sensor[0].get('block_id'), 'sensor_id': sensor[0].get('sensor_id'), 'state': val_state, 'values': values}


@RemoteApp.post('/anturi/aika')
async def get_sensor_data_by_time(input: TimedGet):

    rows = DataSQL.get_instance().Get_Data_Between(input.sensor_id, input.start.strftime('%Y-%m-%dT%H:%M:%S'), input.end.strftime('%Y-%m-%dT%H:%M:%S'))

    return rows

@RemoteApp.get('/anturi/muutokset/{sensor_id}')
async def get_state_changes(sensor_id: str):
    
    rows = StateSQL.get_instance().Get_Data_By_Column('sensor_id', sensor_id)

    return rows


@RemoteApp.delete('/mittaus/{id}', summary='Yksittäisen mittausarvon poisto id:llä why.... median exists')
async def delete_reading(id: int):
    DataSQL.get_instance().Del_Data_By_Column('id', id)
    return {'details': 'successful'}

@RemoteApp.delete('/anturi/{sensor_id}', summary='Anturin poisto')
async def delete_sensor(sensor_id: str):
    DataSQL.get_instance().Del_Data_By_Column('sensor_id', sensor_id)
    BlockSQL.get_instance().Del_Data_By_Column('sensor_id', sensor_id)
    return {'details': 'successful'}
