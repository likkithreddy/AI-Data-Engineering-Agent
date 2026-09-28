from app.db.base import Base
from app.db.engine import engine
from app.models import Customer, Order, OrderItem, Product


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    main()