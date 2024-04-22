from fastapi import FastAPI, HTTPException
from datetime import datetime

from Sensor import SensorData, SensorState, BlockID
from Database import SQLink

# How the F doesnt python have this....
def first(list):
    if len(list) < 1: return None
    return list[0]

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




# Start of HTTP Endpoints

app = FastAPI(
    title='Sensor Management Backend',
    description='Endpoints for getting data from sensors and managing them',
    version='V1.0')


@app.get('/anturit', summary='Listaa kaikki anturit (tunniste, lohko, tila).')
async def get_all_sensors():
    rows = sql2.Get_All_Data()
    return [{'sensor_id': x[1], 'block_id': x[0], 'state': x[2]} for x in rows]


@app.post('/anturit', summary='Lisää uuden anturin järjestelmään.')
async def sensor_add(input: BlockID):
    sql2.Del_Data_By_Column('sensor_id', input.sensor_id)
    sql2.Add_Data([('block_id', input.block_id), 
                ('sensor_id', input.sensor_id),
                ('sensor_state', True)])    
    return {'details': 'successful'}


@app.get('/anturit/{block_id}', summary='Listaa tietyn lohkon kaikki anturit (tunniste, tila, viimeisin mitta-arvo ja aikaleima)')
async def get_sensor_by_block(block_id: str):
    data = sql2.Get_Data_By_Column('block_id', block_id)

    output = [{'sensor_id': x.get('sensor_id'), 'block_id': x.get('block_id'), 'state': x.get('sensor_state')} for x in data]

    for x in output:
        temp = sql.Get_Data_By_Column('sensor_id', x.get('sensor_id'), 'time', 1)

        if len(temp) == 1:
            x['data'] = {'timestamp': first(temp).get('time'), 'temperature': first(temp).get('temperature')}
        else:
            x['data'] = None

    return output

@app.get('/anturi/{sensor_id}', summary='Näyttää yksittäisen anturin kaikki tiedot (tunniste, lohko, tila, mitta-arvot ajanhetkille')
async def get_sensor_state(sensor_id: str):
    sensor = sql2.Get_Data_By_Column('sensor_id', sensor_id)

    if len(sensor) < 1:
        raise HTTPException(status_code=404, detail='sensor not in system')

    rows = sql.Get_Custom_Data(f'''SELECT sensor_id, time, temperature FROM {sql.tablename}
                                    WHERE sensor_id = '{sensor_id}' 
                                    AND time IN (
                                        SELECT min(time)
                                        FROM {sql.tablename}
                                        WHERE sensor_id = '{sensor_id}'
                                        GROUP BY strftime('%Y-%m-%dT%H', time)
                                    )
                                    ORDER BY time
                                    LIMIT 24;''')

    values = [{'timestamp': x.get('time'), 'temperature': x.get('temperature')} for x in rows]

    return {'block_id': first(sensor).get('block_id'), 'sensor_id': first(sensor).get('sensor_id'), 'state': first(sensor).get('sensor_state'), 'values': values}


@app.put('/anturi{sensor_id}', summary='Muuta anturin tila')
async def set_sensor_state(input: SensorState):
    rows = sql2.Get_Data_By_Column('sensor_id', input.sensor_id)

    if len(rows) < 1:
        raise HTTPException(status_code=404, detail='sensor not in system')
    
    sql2.Del_Data_By_Column('sensor_id', input.sensor_id)
    sql2.Add_Data([('block_id', first(rows).get('block_id')), 
                ('sensor_id', first(rows).get('sensor_id')),
                ('sensor_state', input.sensor_state)])   
    return {'detail': 'successful'}


@app.delete('/anturi/data?sensor={sensor_id}&time={time}', summary='Yksittäisen mittausarvon poisto aika muodossa %Y-%m-%dT%H:%M:%S why.... median exists')
async def delete_reading(sensor_id: str, time: str):
    sql.Del_Data_By_Col_Double('sensor_id', sensor_id, 'time', time)
    return {'details': 'successful'}

@app.delete('/anturi/{sensor_id}', summary='Anturin poisto')
async def delete_reading(sensor_id: str):
    sql.Del_Data_By_Column('sensor_id', sensor_id)
    sql2.Del_Data_By_Column('sensor_id', sensor_id)
    return {'details': 'successful'}

@app.post('/add', summary='Lisää järjestelmään anturiarvo')
async def sensor_data(input: SensorData):
    sql.Add_Data([('sensor_id', input.sensor_id), 
                ('time', datetime.now().strftime('%Y-%m-%dT%H:%M:%S')), 
                ('temperature', input.temperature)])
    
    return {'details': 'successful'}












# /anturit:
# GET: Listaa kaikki anturit (tunniste, lohko, tila).
# POST: Lisää uuden anturin järjestelmään.
# /anturit/{lohko}:
# GET: Listaa tietyn lohkon kaikki anturit (tunniste, tila, viimeisin mitta-arvo ja aikaleima).
# /anturi/{tunniste}:
# GET: Näyttää yksittäisen anturin kaikki tiedot (tunniste, lohko, tila, mitta-arvot ajanhetkille).
# PUT: Muuttaa anturin tilaa tai lohkoa.
# DELETE: Poistaa yksittäisen mittatuloksen.
# 
# 
# 
# 
# /tilamuutokset/{tunniste}:
# GET: Näyttää yksittäisen anturin kaikki tilamuutokset ajankohtineen.
# /tila/{tila}:
# GET: Hakee anturit niiden nykyisen tilan mukaan (tunniste, lohko, tila).
# /virheet:
# GET: Näyttää graafin virhetilanteiden esiintymisajankohdista.