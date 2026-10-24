import sqlite3
import pytest
from backend.analytics import run_analytics
from backend.interpreter import interpret_question

@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.execute("""CREATE TABLE sales (
        transaction_id TEXT, order_date TEXT, product TEXT, category TEXT,
        region TEXT, sales_channel TEXT, quantity INTEGER, unit_price REAL,
        discount_amount REAL, status TEXT
    )""")
    c.executemany("INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
        ("1", "2026-01-03", "Mouse", "Accessories", "North", "Online", 2, 100, 0, "Completed"),
        ("2", "2026-01-04", "Chair", "Furniture", "South", "Retail", 1, 300, 20, "Completed"),
        ("3", "2026-02-04", "Mouse", "Accessories", "North", "Online", 3, 100, 0, "Completed"),
        ("4", "2026-02-05", "Monitor", "Electronics", "West", "Retail", 1, 500, 0, "Returned"),
        ("5", "2026-02-06", "Broken", "Other", "East", "Online", 1, None, 0, "Completed"),
        ("6", "2026-02-07", "ZeroQty", "Other", "East", "Online", 0, 100, 0, "Completed"),
    ])
    c.commit()
    yield c
    c.close()

def test_total_revenue_excludes_returned_missing_price_and_zero_quantity(conn):
    result = run_analytics(conn, "total_revenue")
    assert result["supporting_data"][0]["total_revenue"] == 780.0

def test_top_product(conn):
    result = run_analytics(conn, "top_product")
    assert result["supporting_data"][0]["product"] == "Mouse"

def test_monthly_trend(conn):
    result = run_analytics(conn, "monthly_trend")
    assert [r["month"] for r in result["supporting_data"]] == ["2026-01", "2026-02"]

def test_month_comparison(conn):
    result = run_analytics(conn, "revenue_comparison", {"month_a": "2026-01", "month_b": "2026-02"})
    assert result["summary"]["absolute_change"] == -180.0

def test_invalid_intent_rejected(conn):
    with pytest.raises(ValueError):
        run_analytics(conn, "delete_everything")

def test_interpreter_maps_region_question():
    assert interpret_question("Which region generated the highest sales?")["intent"] == "top_region"

def test_blank_question_rejected():
    with pytest.raises(ValueError):
        interpret_question("   ")
