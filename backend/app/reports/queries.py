from app.db.database import get_connection


def _rows_to_dicts(rows):
    return [dict(row) for row in rows]


def get_report_data():
    with get_connection() as connection:
        summary = connection.execute(
            """
            SELECT
                COUNT(*) AS total_orders,
                COALESCE(SUM(amount), 0) AS total_revenue,
                COALESCE(AVG(amount), 0) AS average_order_value
            FROM orders
            """
        ).fetchone()

        top_products = connection.execute(
            """
            SELECT
                product,
                COUNT(*) AS order_count,
                ROUND(SUM(amount), 2) AS revenue
            FROM orders
            GROUP BY product
            ORDER BY revenue DESC
            LIMIT 5
            """
        ).fetchall()

        orders_by_day = connection.execute(
            """
            SELECT
                created_at AS day,
                COUNT(*) AS order_count,
                ROUND(SUM(amount), 2) AS revenue
            FROM orders
            WHERE created_at >= date('now', '-6 days')
            GROUP BY created_at
            ORDER BY created_at
            """
        ).fetchall()

        rows = connection.execute(
            """
            SELECT id, customer, product, amount, created_at
            FROM orders
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()

    return {
        "summary": {
            "total_orders": summary["total_orders"],
            "total_revenue": round(summary["total_revenue"], 2),
            "average_order_value": round(summary["average_order_value"], 2),
        },
        "top_products": _rows_to_dicts(top_products),
        "orders_by_day": _rows_to_dicts(orders_by_day),
        "rows": _rows_to_dicts(rows),
    }
