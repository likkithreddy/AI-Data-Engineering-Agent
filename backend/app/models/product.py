from decimal import Decimal

from sqlalchemy import CheckConstraint, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    __table_args__ = (
        CheckConstraint(
            "unit_price >= 0",
            name="ck_products_unit_price_non_negative",
        ),
        CheckConstraint(
            "cost >= 0",
            name="ck_products_cost_non_negative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="product",
    )