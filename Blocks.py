from pydantic import BaseModel

class BlockID(BaseModel):
    sensor_id: str
    block_id: str