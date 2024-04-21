from pydantic import BaseModel

class SensorData(BaseModel):
    sensor_id: str
    temperature: float
    error_state: bool

