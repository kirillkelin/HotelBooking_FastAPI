from datetime import date

from sqlalchemy import and_, func, select
from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.hotels.rooms.models import Rooms
from app.database import async_session_maker, engine


class RoomDAO(BaseDAO):
    model = Rooms
    
    @classmethod
    async def find_all(cls, hotel_id: int, date_from: date, date_to: date):
        """
        WITH booked_rooms AS(
            SELECT room_id, COUNT(room_id) AS occupied_rooms
            FROM bookings
            WHERE date_from <= '2023-06-20' and date_to >= '2023-05-15'
            GROUP BY room_id
        ),

        get_rooms_by_id AS(
            SELECT rooms.id, (rooms.quantity - COALESCE(occupied_rooms,0)) AS rooms_left
            FROM rooms
            LEFT JOIN booked_rooms ON Rooms.id = booked_rooms.room_id
            WHERE hotel_id = 1
            GROUP BY rooms.id, (rooms.quantity - COALESCE(occupied_rooms,0))
        )
        SELECT *
        FROM get_hotel
        """
        booked_rooms = select(Bookings.room_id, func.count(Bookings.room_id).label("occupied_rooms")).select_from(Bookings).where(and_(Bookings.date_from <= date_to, Bookings.date_to >= date_from)).group_by(Bookings.room_id).cte("booked_rooms")

        get_rooms_by_id = select(Rooms.__table__.columns, (Rooms.price * (date_to - date_from).days).label("total_cost"), (Rooms.quantity - func.coalesce(booked_rooms.c.occupied_rooms, 0)).label("rooms_left")).select_from(Rooms).join(booked_rooms, Rooms.id == booked_rooms.c.room_id, isouter=True).where(Rooms.hotel_id == hotel_id)

        async with async_session_maker() as sessesion:
            #print(get_hotels_with_rooms_left.compile(engine, compile_kwargs={"literal_binds":True}))
            rooms = await sessesion.execute(get_rooms_by_id)
            return rooms.mappings().all()


