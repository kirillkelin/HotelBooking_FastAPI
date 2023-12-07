from datetime import date

from sqlalchemy import and_, func, select

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker, engine
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms


class HotelDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def find_all(cls, location: str, date_from: date, date_to: date):
        """
        WITH booked_rooms AS(
            SELECT room_id, COUNT(room_id) AS occupied_rooms
            FROM bookings
            WHERE date_from <= '2023-06-20' and date_to >= '2023-05-15'
            GROUP BY room_id
        ),

        booked_hotels AS(
            SELECT hotel_id, SUM(quantity - COALESCE(occupied_rooms,0)) as rooms_left
            FROM rooms
            LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
            GROUP BY hotel_id
        )
        SELECT *
        FROM hotels
        LEFT JOIN booked_hotels ON hotels.id = booked_hotels.hotel_id
        WHERE location LIKE '%Алтай%' AND rooms_left >=1
        """
        booked_rooms = (
            select(
                Bookings.room_id, func.count(Bookings.room_id).label("occupied_rooms")
            )
            .select_from(Bookings)
            .where(and_(Bookings.date_from <= date_to, Bookings.date_to >= date_from))
            .group_by(Bookings.room_id)
            .cte("booked_rooms")
        )

        booked_hotels = (
            select(
                Rooms.hotel_id,
                func.sum(
                    Rooms.quantity - func.coalesce(booked_rooms.c.occupied_rooms, 0)
                ).label("rooms_left"),
            )
            .select_from(Rooms)
            .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
            .group_by(Rooms.hotel_id)
            .cte("booked_hotels")
        )

        get_hotels_with_rooms_left = (
            select(Hotels.__table__.columns, booked_hotels.c.rooms_left)
            .select_from(Hotels)
            .join(booked_hotels, Hotels.id == booked_hotels.c.hotel_id, isouter=True)
            .where(
                and_(
                    Hotels.location.like(f"%{location}%"),
                    booked_hotels.c.rooms_left >= 1,
                )
            )
        )

        async with async_session_maker() as session:
            # print(get_hotels_with_rooms_left.compile(engine, compile_kwargs={"literal_binds":True}))
            hotels_with_rooms_left = await session.execute(get_hotels_with_rooms_left)
            return hotels_with_rooms_left.mappings().all()
