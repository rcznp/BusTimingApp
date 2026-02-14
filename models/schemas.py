from pydantic import BaseModel
from typing import List
from datetime import datetime


class Arrival(BaseModel):
    estimated_arrival: datetime   # ← add this
    eta_minutes: int
    status: str
    load: str


class Service(BaseModel):
    service_no: str
    arrivals: List[Arrival]


class BusArrivalResponse(BaseModel):
    bus_stop_code: str
    timestamp: datetime
    services: List[Service]