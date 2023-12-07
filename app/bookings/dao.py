from datetime import date

from sqlalchemy import and_, func, insert, select
from sqlalchemy.exc import SQLAlchemyError

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker, engine
from app.hotels.rooms.models import Rooms
from app.logger import logger


class BookingDAO(BaseDAO):
    model = Bookings

    @classmethod
    async def find_all_with_info(cls, user_id: int):
        """
        SELECT bookings.room_id, bookings.user_id, bookings.date_from, bookings.date_to, bookings.price,
        bookings.total_cost, bookings.total_days, rooms.image_id, rooms.name, rooms.description, rooms.services
        FROM bookings
        LEFT JOIN rooms ON rooms.id = bookings.room_id
        WHERE bookings.user_id = 5
        """
        info = (
            select(
                Bookings.id,
                Bookings.room_id,
                Bookings.user_id,
                Bookings.date_from,
                Bookings.date_to,
                Bookings.price,
                Bookings.total_cost,
                Bookings.total_days,
                Rooms.image_id,
                Rooms.name,
                Rooms.description,
                Rooms.services,
            )
            .select_from(Bookings)
            .join(Rooms, Rooms.id == Bookings.room_id, isouter=True)
            .where(Bookings.user_id == user_id)
        )

        async with async_session_maker() as sessesion:
            # print(info.compile(engine, compile_kwargs={"literal_binds":True}))
            result_query = await sessesion.execute(info)
            return result_query.mappings().all()

    @classmethod
    async def add(
        cls,
        user_id: int,
        room_id: int,
        date_from: date,
        date_to: date,
    ):
        """
        with booked_room as (
        select * from bookings
        where room_id = 1 and
        (date_to >= '2023-05-15' and
        date_from <= '2023-06-20'))

        select rooms.quantity - count(booked_rooms.room_id) from rooms
        left join booked_rooms on booked_rooms.room_id = rooms.id
        where rooms.id = 1
        group by rooms.quantity, booked_rooms.room_id
        """
        booked_rooms = (
            select(Bookings)
            .where(
                and_(
                    Bookings.room_id == room_id,
                    Bookings.date_to >= date_from,
                    Bookings.date_from <= date_to,
                )
            )
            .cte("booked_rooms")
        )

        get_rooms_left = (
            select(
                Rooms.quantity - func.count(booked_rooms.c.room_id).label("rooms_left")
            )
            .select_from(Rooms)
            .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
            .where(Rooms.id == room_id)
            .group_by(Rooms.quantity, booked_rooms.c.room_id)
        )

        try:
            async with async_session_maker() as sessesion:
                # print(get_rooms_left.compile(engine, compile_kwargs={"literal_binds":True}))
                rooms_left = await sessesion.execute(get_rooms_left)
                rooms_left: int = rooms_left.scalar()

                if rooms_left > 0:
                    get_price = select(Rooms.price).filter_by(id=room_id)
                    price = await sessesion.execute(get_price)
                    price: int = price.scalar()
                    add_booking = (
                        insert(Bookings)
                        .values(
                            room_id=room_id,
                            user_id=user_id,
                            date_from=date_from,
                            date_to=date_to,
                            price=price,
                        )
                        .returning(
                            Bookings.id,
                            Bookings.room_id,
                            Bookings.user_id,
                            Bookings.date_from,
                            Bookings.date_to,
                            Bookings.price,
                            Bookings.total_cost,
                            Bookings.total_days,
                        )
                    )
                    new_booking = await sessesion.execute(add_booking)
                    await sessesion.commit()
                    return new_booking.mappings().one()
                else:
                    return None
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            elif isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": Cannot add booking"
            extra = {
                "user_id": user_id,
                "room_id": room_id,
                "date_from": date_from,
                "date_to": date_to,
            }
            logger.error(msg, extra=extra, exc_info=True)
