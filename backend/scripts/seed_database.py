from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.engine import engine
from app.models import Customer, Order, OrderItem, Product


def seed_database() -> None:
    with Session(engine) as session:
        existing_customer = session.scalar(
            select(Customer).limit(1)
        )

        if existing_customer:
            print("Database already contains data. Skipping seed.")
            return

        products = [
            Product(
                name="Laptop Pro 14",
                category="Electronics",
                unit_price=Decimal("1299.00"),
                cost=Decimal("850.00"),
            ),
            Product(
                name="Wireless Headphones",
                category="Electronics",
                unit_price=Decimal("199.00"),
                cost=Decimal("110.00"),
            ),
            Product(
                name="Office Chair",
                category="Furniture",
                unit_price=Decimal("349.00"),
                cost=Decimal("210.00"),
            ),
            Product(
                name="Standing Desk",
                category="Furniture",
                unit_price=Decimal("599.00"),
                cost=Decimal("350.00"),
            ),
            Product(
                name="Notebook Pack",
                category="Office Supplies",
                unit_price=Decimal("24.00"),
                cost=Decimal("8.00"),
            ),
            Product(
                name="Mechanical Keyboard",
                category="Electronics",
                unit_price=Decimal("129.00"),
                cost=Decimal("70.00"),
            ),
        ]

        session.add_all(products)
        session.flush()

        customers = [
            Customer(
                name="Alice Johnson",
                email="alice@example.com",
                country="USA",
                signup_date=date(2024, 1, 15),
                customer_segment="Enterprise",
            ),
            Customer(
                name="Bob Smith",
                email="bob@example.com",
                country="UK",
                signup_date=date(2024, 3, 20),
                customer_segment="SMB",
            ),
            Customer(
                name="Carlos Garcia",
                email="carlos@example.com",
                country="Spain",
                signup_date=date(2024, 5, 10),
                customer_segment="Consumer",
            ),
            Customer(
                name="Diana Patel",
                email="diana@example.com",
                country="India",
                signup_date=date(2024, 7, 1),
                customer_segment="Enterprise",
            ),
            Customer(
                name="Ethan Brown",
                email="ethan@example.com",
                country="USA",
                signup_date=date(2024, 8, 12),
                customer_segment="SMB",
            ),
        ]

        session.add_all(customers)
        session.flush()

        orders = [
            Order(
                customer_id=customers[0].id,
                order_date=date(2025, 1, 10),
                status="completed",
            ),
            Order(
                customer_id=customers[1].id,
                order_date=date(2025, 2, 15),
                status="completed",
            ),
            Order(
                customer_id=customers[2].id,
                order_date=date(2025, 3, 5),
                status="completed",
            ),
            Order(
                customer_id=customers[3].id,
                order_date=date(2025, 4, 18),
                status="completed",
            ),
            Order(
                customer_id=customers[4].id,
                order_date=date(2025, 5, 22),
                status="completed",
            ),
            Order(
                customer_id=customers[0].id,
                order_date=date(2025, 7, 8),
                status="completed",
            ),
            Order(
                customer_id=customers[1].id,
                order_date=date(2025, 9, 12),
                status="cancelled",
            ),
            Order(
                customer_id=customers[3].id,
                order_date=date(2025, 10, 3),
                status="pending",
            ),
        ]

        session.add_all(orders)
        session.flush()

        order_items = [
            OrderItem(
                order_id=orders[0].id,
                product_id=products[0].id,
                quantity=2,
                unit_price=products[0].unit_price,
                discount=Decimal("0.05"),
            ),
            OrderItem(
                order_id=orders[0].id,
                product_id=products[1].id,
                quantity=3,
                unit_price=products[1].unit_price,
                discount=Decimal("0.00"),
            ),
            OrderItem(
                order_id=orders[1].id,
                product_id=products[2].id,
                quantity=2,
                unit_price=products[2].unit_price,
                discount=Decimal("0.10"),
            ),
            OrderItem(
                order_id=orders[2].id,
                product_id=products[4].id,
                quantity=10,
                unit_price=products[4].unit_price,
                discount=Decimal("0.00"),
            ),
            OrderItem(
                order_id=orders[3].id,
                product_id=products[3].id,
                quantity=3,
                unit_price=products[3].unit_price,
                discount=Decimal("0.05"),
            ),
            OrderItem(
                order_id=orders[4].id,
                product_id=products[5].id,
                quantity=5,
                unit_price=products[5].unit_price,
                discount=Decimal("0.00"),
            ),
            OrderItem(
                order_id=orders[5].id,
                product_id=products[3].id,
                quantity=4,
                unit_price=products[3].unit_price,
                discount=Decimal("0.08"),
            ),
            OrderItem(
                order_id=orders[6].id,
                product_id=products[0].id,
                quantity=1,
                unit_price=products[0].unit_price,
                discount=Decimal("0.00"),
            ),
            OrderItem(
                order_id=orders[7].id,
                product_id=products[2].id,
                quantity=1,
                unit_price=products[2].unit_price,
                discount=Decimal("0.00"),
            ),
        ]

        session.add_all(order_items)

        session.commit()

        print("Database seeded successfully.")


if __name__ == "__main__":
    seed_database()