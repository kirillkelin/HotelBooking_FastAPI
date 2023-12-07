from typing import List, Optional

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Rooms(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    name: Mapped[str]
    description: Mapped[Optional[str]]
    price: Mapped[int]
    services: Mapped[Optional[list[str]]] = mapped_column(JSON)
    quantity: Mapped[int]
    image_id: Mapped[int]

    booking: Mapped[List["Bookings"]] = relationship(back_populates="room")
    hotel: Mapped["Hotels"] = relationship(back_populates="rooms")

    def __str__(self) -> str:
        return f"Номер {self.name}"
