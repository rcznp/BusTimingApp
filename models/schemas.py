from pydantic import BaseModel
from typing import List
class Arrival(BaseModel):
    eta_minutes: int
    status: str
    load: str

class Service(BaseModel):
    service_no: str
    arrivals: List[Arrival]

class BusArrivalResponse(BaseModel):
    bus_stop_code: str
    timestamp: str
    services: List[Service]