from pathlib import Path
import sqlite3
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = PROJECT_ROOT / "data" / "sales_data.csv"
DEFAULT_DB = PROJECT_ROOT / "sales.db"

EXPECTED_COLUMNS = [
    "Transaction_Id", "Order_date", "Product", "Category", "Region",
    "Sales_channel", "Quantity", "Unit_price", "Discount_amount", "Status"
]

def get_connection(db_path: str | Path = DEFAULT_DB) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_database(csv_path: str | Path = DEFAULT_CSV, db_path: str | Path = DEFAULT_DB) -> dict:
    df = pd.read_csv(csv_path)
    missing_columns = sorted(set(EXPECTED_COLUMNS) - set(df.columns))
    if missing_columns:
        raise ValueError(f"CSV is missing required columns: {', '.join(missing_columns)}")

    df = df[EXPECTED_COLUMNS].copy()
    df["Order_date"] = pd.to_datetime(df["Order_date"], format="%d-%m-%Y", errors="coerce")
    for col in ["Quantity", "Unit_price", "Discount_amount"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Status"] = df["Status"].astype("string").str.strip()
    for col in ["Transaction_Id", "Product", "Category", "Region", "Sales_channel"]:
        df[col] = df[col].astype("string").str.strip()

    # Keep rows with valid ID, date, product, region, quantity and discount.
    # Missing/invalid unit price is retained as NULL and excluded by analytics.
    required = ["Transaction_Id", "Order_date", "Product", "Region", "Quantity", "Discount_amount", "Status"]
    valid = df[required].notna().all(axis=1) & (df["Quantity"] >= 0) & (df["Discount_amount"] >= 0)
    cleaned = df.loc[valid].copy()
    cleaned["Order_date"] = cleaned["Order_date"].dt.strftime("%Y-%m-%d")
    cleaned["Unit_price"] = cleaned["Unit_price"].where(cleaned["Unit_price"] >= 0)
    cleaned.loc[cleaned["Unit_price"].isna(), "Unit_price"] = None

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection(db_path)
    with conn:
        conn.execute("DROP TABLE IF EXISTS sales")
        conn.execute("""
            CREATE TABLE sales (
                transaction_id TEXT PRIMARY KEY,
                order_date TEXT NOT NULL,
                product TEXT NOT NULL,
                category TEXT,
                region TEXT NOT NULL,
                sales_channel TEXT,
                quantity INTEGER NOT NULL CHECK(quantity >= 0),
                unit_price REAL CHECK(unit_price IS NULL OR unit_price >= 0),
                discount_amount REAL NOT NULL CHECK(discount_amount >= 0),
                status TEXT NOT NULL
            )
        """)
        conn.executemany("""
            INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (
                str(r.Transaction_Id), str(r.Order_date), str(r.Product),
                None if pd.isna(r.Category) else str(r.Category),
                str(r.Region), None if pd.isna(r.Sales_channel) else str(r.Sales_channel),
                int(r.Quantity), None if pd.isna(r.Unit_price) else float(r.Unit_price),
                float(r.Discount_amount), str(r.Status)
            )
            for r in cleaned.itertuples(index=False)
        ])
    conn.close()
    return {
        "input_rows": int(len(df)),
        "loaded_rows": int(len(cleaned)),
        "invalid_rows_removed": int(len(df) - len(cleaned)),
        "missing_or_invalid_unit_prices": int(cleaned["Unit_price"].isna().sum()),
        "database_path": str(db_path)
    }
