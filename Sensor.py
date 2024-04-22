from pydantic import BaseModel

class SensorData(BaseModel):
    sensor_id: str
    temperature: float

class SensorState(BaseModel):
    sensor_id: str
    sensor_state: bool

class BlockID(BaseModel):
    sensor_id: str
    block_id: str