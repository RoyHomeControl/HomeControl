from pydantic import BaseModel


class WindRequest(BaseModel):
    wind: int

class TemperatureRequest(BaseModel):
    temp: int