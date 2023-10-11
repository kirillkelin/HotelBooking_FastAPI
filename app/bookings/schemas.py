from datetime import date
from typing import List, Optional
from pydantic import BaseModel


class SBooking(BaseModel):
    id: int
    room_id: int
    user_id: int
    date_from: date
    date_to: date
    price: int
    total_cost: int
    total_days: int

    class Config:
        from_attributes = True

class SBookingwithoutid(BaseModel):
    room_id: int
    user_id: int
    date_from: date
    date_to: date
    price: int
    total_cost: int
    total_days: int

    class Config:
        from_attributes = True

class SBookingInfo(SBookingwithoutid):
    image_id: int
    name: str
    description: Optional[str]
    services: Optional[List[str]]