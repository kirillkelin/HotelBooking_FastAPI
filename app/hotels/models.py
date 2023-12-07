from typing import List, Optional
from sqlalchemy import JSON
from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Hotels(Base):
    __tablename__ = "hotels"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    location: Mapped[str]
    services: Mapped[Optional[list[str]]] = mapped_column(JSON)
    rooms_quantity: Mapped[int]
    image_id: Mapped[Optional[int]]

    rooms: Mapped[List["Rooms"]] = relationship(back_populates="hotel")

    def __str__(self):
        return f"Отель {self.name}"
