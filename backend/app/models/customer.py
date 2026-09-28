from datetime import date

from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    country: Mapped[str] = mapped_column(String(80), nullable=False)
    signup_date: Mapped[date] = mapped_column(Date, nullable=False)
    customer_segment: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    orders: Mapped[list["Order"]] = relationship(
        back_populates="customer",
    )