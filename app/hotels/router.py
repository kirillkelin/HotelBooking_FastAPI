from datetime import date
from typing import Optional
from fastapi import APIRouter
from app.exceptions import CannotBookForLongPeriod, DateFromCannotBeAfterDateTo

from app.hotels.dao import HotelDAO
from app.hotels.schemas import SHotelInfo, SHotels
from fastapi_cache.decorator import cache


router = APIRouter(
    prefix="/hotels",
    tags=["Отели"],
)


@router.get("/{location}")
@cache(expire=20)
async def get_hotel(location: str, date_from: date, date_to: date) -> list[SHotelInfo]:
    if date_from > date_to:
        raise DateFromCannotBeAfterDateTo
    elif (date_to - date_from).days > 31:
        raise CannotBookForLongPeriod
    hotels = await HotelDAO.find_all(location, date_from, date_to)
    return hotels

@router.get("/id/{hotel_id}", include_in_schema=True)
async def get_hotel_by_id(hotel_id: int) -> Optional[SHotels]:
    return await HotelDAO.find_one_or_none(id=hotel_id)