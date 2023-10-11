from datetime import date
from typing import Optional
from fastapi import APIRouter
from app.exceptions import DateFromCannotBeAfterDateTo

from app.hotels.dao import HotelDAO
from app.hotels.schemas import SHotelInfo, SHotels


router = APIRouter(
    prefix="/hotels",
    tags=["Отели"],
)


@router.get("/{location}")
async def get_hotel(location: str, date_from: date, date_to: date) -> list[SHotelInfo]:
    if date_from > date_to:
        raise DateFromCannotBeAfterDateTo
    hotels = await HotelDAO.find_all(location, date_from, date_to)
    return hotels

@router.get("/id/{hotel_id}", include_in_schema=True)
async def get_hotel_by_id(hotel_id: int) -> Optional[SHotels]:
    return await HotelDAO.find_one_or_none(id=hotel_id)