import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env")

DB_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

engine = create_engine(DB_URL)


def load_to_staging(data):
    with engine.connect() as conn:
        for name, df in data.items():
            table_name = f"stg_{name}"
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            conn.commit()
            print(f"{table_name}: загружено {len(df)} строк")


def test_connection():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"подключение к БД: ок")


def load_to_dwh(data):
    with engine.connect() as conn:
        for t in ["fact_events", "fact_payments", "fact_orders",
                   "dim_customers", "dim_products", "dim_date"]:
            conn.execute(text(f"TRUNCATE TABLE {t} CASCADE"))
        conn.commit()
        dates = set()
        for name in ["orders", "payments", "events"]:
            df = data[name]
            ts_col = {
                "orders": "order_timestamp",
                "payments": "payment_timestamp",
                "events": "event_timestamp",
            }[name]
            dates.update(df[ts_col].dt.date.dropna().unique())

        dim_date = pd.DataFrame(sorted(dates), columns=["date_id"])
        dim_date["date_id"] = pd.to_datetime(dim_date["date_id"])
        dim_date["day"] = dim_date["date_id"].dt.day
        dim_date["month"] = dim_date["date_id"].dt.month
        dim_date["year"] = dim_date["date_id"].dt.year
        dim_date["weekday"] = dim_date["date_id"].dt.weekday
        dim_date["month_name"] = dim_date["date_id"].dt.strftime("%B")
        dim_date.to_sql("dim_date", conn, if_exists="append", index=False)
        conn.commit()
        print(f"dim_date: {len(dim_date)} дат")

        data["customers"].to_sql("dim_customers", conn, if_exists="append", index=False)
        conn.commit()
        print(f"dim_customers: {len(data['customers'])} строк")

        data["products"].to_sql("dim_products", conn, if_exists="append", index=False)
        conn.commit()
        print(f"dim_products: {len(data['products'])} строк")

        orders = data["orders"].copy()
        orders["date_id"] = orders["order_timestamp"].dt.date
        orders["total_amount"] = orders["quantity"] * orders["unit_price"]
        orders = orders.drop(columns=["order_timestamp"])
        orders.to_sql("fact_orders", conn, if_exists="append", index=False)
        conn.commit()
        print(f"fact_orders: {len(orders)} строк")

        payments = data["payments"].copy()
        payments["date_id"] = payments["payment_timestamp"].dt.date
        payments = payments.drop(columns=["payment_timestamp"])
        payments.to_sql("fact_payments", conn, if_exists="append", index=False)
        conn.commit()
        print(f"fact_payments: {len(payments)} строк")

        events = data["events"].copy()
        events["date_id"] = events["event_timestamp"].dt.date
        events = events.drop(columns=["event_timestamp"])
        events.to_sql("fact_events", conn, if_exists="append", index=False)
        conn.commit()
        print(f"fact_events: {len(events)} строк")


if __name__ == "__main__":
    test_connection()