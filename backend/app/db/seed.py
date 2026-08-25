import random   # noqa: I001
from datetime import date, timedelta

from app.db.database import get_connection, initialize_database


CUSTOMERS = [
    "Amina",
    "Omar",
    "Layla",
    "Zayd",
    "Mariam",
    "Noor",
    "Yusuf",
    "Sara",
]

PRODUCTS = [
    "Laptop Stand",
    "Wireless Mouse",
    "USB-C Hub",
    "Mechanical Keyboard",
    "Desk Lamp",
    "Notebook Set",
]


def main():
    initialize_database()
    random.seed(42)

    today = date.today() 
    rows = []

    for _ in range(200):
        created_at = today - timedelta(days=random.randint(0, 29))
        rows.append(
            (
                random.choice(CUSTOMERS),
                random.choice(PRODUCTS),
                round(random.uniform(5, 200), 2),
                created_at.isoformat(),
            )
        )

    with get_connection() as connection:
        connection.execute("DELETE FROM orders")
        connection.execute("DELETE FROM reports")
        connection.executemany(
            """
            INSERT INTO orders (customer, product, amount, created_at)
            VALUES (?, ?, ?, ?)
            """,
            rows,
        )
        connection.commit()

        count = connection.execute("SELECT COUNT(*) AS count FROM orders").fetchone()[
            "count"
        ]

    print(f"Seeded {count} orders into report.db")


if __name__ == "__main__":
    main()
