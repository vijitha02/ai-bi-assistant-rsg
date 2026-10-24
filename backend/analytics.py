from __future__ import annotations

from datetime import datetime
from typing import Any
import sqlite3

SUPPORTED_INTENTS = {
    "total_revenue",
    "top_product",
    "monthly_trend",
    "top_region",
    "revenue_comparison",
    "total_units",
    "total_discounts",
    "transaction_count",
    "average_order_value",
    "top_selling_product",
}
def _rows(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
    conn.row_factory = sqlite3.Row
    return [dict(row) for row in conn.execute(sql, params).fetchall()]

def run_analytics(conn: sqlite3.Connection, intent: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Run only predefined, read-only analytical queries."""
    params = params or {}
    if intent not in SUPPORTED_INTENTS:
        raise ValueError("Unsupported question. Try one of the suggested questions.")

    # Revenue policy: Completed transactions only; rows with missing/invalid prices
    # and non-positive quantities are excluded. Net revenue = quantity * unit price - discount.
    base = """
        FROM sales
        WHERE LOWER(TRIM(status)) = 'completed'
          AND unit_price IS NOT NULL AND unit_price >= 0
          AND quantity > 0
    """
    
    if intent == "total_units":
        rows = _rows(conn, f"""
            SELECT COALESCE(SUM(quantity), 0) AS total_units
            {base}
        """)
        return {
            "intent": intent,
            "answer": f"Total units sold: {rows[0]['total_units']:,.0f}.",
            "supporting_data": rows,
            "metric": "total_units_sold",
        }

    if intent == "total_discounts":
        rows = _rows(conn, f"""
            SELECT ROUND(COALESCE(SUM(discount_amount), 0), 2)
                   AS total_discounts
            {base}
        """)
        return {
            "intent": intent,
            "answer": f"Total discounts: {rows[0]['total_discounts']:,.2f}.",
            "supporting_data": rows,
            "metric": "total_discounts",
        }

    if intent == "transaction_count":
        rows = _rows(conn, f"""
            SELECT COUNT(*) AS transaction_count
            {base}
        """)
        return {
            "intent": intent,
            "answer": (
                f"Number of eligible completed sales records: "
                f"{rows[0]['transaction_count']:,}."
            ),
            "supporting_data": rows,
            "metric": "transaction_count",
        }

    if intent == "average_order_value":
        rows = _rows(conn, f"""
            SELECT
                ROUND(
                    COALESCE(SUM(quantity * unit_price - discount_amount), 0)
                    / NULLIF(COUNT(*), 0),
                    2
                ) AS average_order_value,
                COUNT(*) AS included_transactions
            {base}
        """)
        value = rows[0]["average_order_value"]
        answer = (
            "Average net revenue per eligible sales record: "
            f"{value:,.2f}."
            if value is not None
            else "Average order value is unavailable because there are no eligible sales records."
        )
        return {
            "intent": intent,
            "answer": answer,
            "supporting_data": rows,
            "metric": "average_order_value",
        }

    if intent == "top_selling_product":
        rows = _rows(conn, f"""
            SELECT product, SUM(quantity) AS units_sold
            {base}
            GROUP BY product
            ORDER BY units_sold DESC, product ASC
            LIMIT 1
        """)
        if not rows:
            raise ValueError("No eligible sales records were found.")
        r = rows[0]
        return {
            "intent": intent,
            "answer": (
                f"{r['product']} is the top-selling product "
                f"with {r['units_sold']:,.0f} units sold."
            ),
            "supporting_data": rows,
            "metric": "units_sold_by_product",
        }

    if intent == "total_revenue":
        rows = _rows(conn, f"""
            SELECT ROUND(SUM(quantity * unit_price - discount_amount), 2) AS total_revenue,
                   COUNT(*) AS included_transactions
            {base}
        """)
        return {"intent": intent, "answer": f"Total net revenue is {rows[0]['total_revenue']:,.2f}.",
                "supporting_data": rows, "metric": "net_revenue"}

    if intent == "top_product":
        rows = _rows(conn, f"""
            SELECT product, ROUND(SUM(quantity * unit_price - discount_amount), 2) AS revenue,
                   SUM(quantity) AS units_sold
            {base}
            GROUP BY product ORDER BY revenue DESC, product ASC LIMIT 1
        """)
        if not rows:
            raise ValueError("No eligible sales records were found.")
        r = rows[0]
        return {"intent": intent, "answer": f"{r['product']} generated the highest net revenue: {r['revenue']:,.2f}.",
                "supporting_data": rows, "metric": "net_revenue_by_product"}

    if intent == "monthly_trend":
        rows = _rows(conn, f"""
            SELECT strftime('%Y-%m', order_date) AS month,
                   ROUND(SUM(quantity * unit_price - discount_amount), 2) AS revenue
            {base}
            GROUP BY strftime('%Y-%m', order_date) ORDER BY month
        """)
        return {"intent": intent, "answer": "Here is the monthly net revenue trend.",
                "supporting_data": rows, "metric": "monthly_net_revenue"}

    if intent == "top_region":
        rows = _rows(conn, f"""
            SELECT region, ROUND(SUM(quantity * unit_price - discount_amount), 2) AS revenue
            {base}
            GROUP BY region ORDER BY revenue DESC, region ASC LIMIT 1
        """)
        if not rows:
            raise ValueError("No eligible sales records were found.")
        r = rows[0]
        return {"intent": intent, "answer": f"{r['region']} generated the highest net sales: {r['revenue']:,.2f}.",
                "supporting_data": rows, "metric": "net_revenue_by_region"}

    if intent == "revenue_comparison":
        month_a = params.get("month_a")
        month_b = params.get("month_b")
        if not month_a or not month_b:
            raise ValueError("For a month comparison, include two months, for example: 'Compare January 2026 and February 2026'.")
        for month in (month_a, month_b):
            try:
                datetime.strptime(month, "%Y-%m")
            except (TypeError, ValueError):
                raise ValueError("Months must use YYYY-MM format, for example 2026-01.")
        rows = _rows(conn, f"""
            SELECT strftime('%Y-%m', order_date) AS month,
                   ROUND(SUM(quantity * unit_price - discount_amount), 2) AS revenue
            {base}
              AND strftime('%Y-%m', order_date) IN (?, ?)
            GROUP BY strftime('%Y-%m', order_date) ORDER BY month
        """, (month_a, month_b))
        values = {r["month"]: r["revenue"] or 0 for r in rows}
        a, b = values.get(month_a, 0), values.get(month_b, 0)
        delta = round(b - a, 2)
        pct = round((delta / a) * 100, 2) if a else None
        comparison = [{"month": month_a, "revenue": a}, {"month": month_b, "revenue": b}]
        if pct is None:
            change_text = f"Revenue changed by {delta:,.2f}; percentage change is unavailable because the first month's revenue is zero."
        else:
            direction = "increased" if delta > 0 else "decreased" if delta < 0 else "did not change"
            change_text = f"Revenue {direction} by {abs(delta):,.2f} ({abs(pct):.2f}%) from {month_a} to {month_b}."
        return {"intent": intent, "answer": change_text, "supporting_data": comparison,
                "metric": "monthly_net_revenue_comparison",
                "summary": {"absolute_change": delta, "percentage_change": pct}}
