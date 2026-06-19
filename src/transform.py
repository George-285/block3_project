import pandas as pd
from pathlib import Path


LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

bad_records = []


def log_bad(source, record_id, reason, row_data=None):
    bad_records.append({
        "source": source,
        "record_id": record_id,
        "reason": reason,
    })


def save_log():
    if bad_records:
        df = pd.DataFrame(bad_records)
        df.to_csv(LOG_DIR / "bad_records.csv", index=False, encoding="utf-8-sig")
        print(f"\nзаписано {len(df)} проблемных записей в logs/bad_records.csv")
    else:
        print("\nпроблемных записей не найдено")


def transform_customers(df):
    df = df.copy()
    df["phone"] = df["phone"].replace("UNKNOWN", pd.NA)
    df["phone"] = df["phone"].astype(str).str.strip()
    df["phone"] = df["phone"].replace(["", "nan", "<NA>"], pd.NA)
    df["email"] = df["email"].str.strip().str.lower()
    df["full_name"] = df["full_name"].str.strip()
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

    nulls = df[df["customer_id"].isna()]
    for _, row in nulls.iterrows():
        log_bad("customers", row.get("customer_id"), "пустой customer_id")
    df = df.dropna(subset=["customer_id"])

    df["phone"] = df["phone"].astype(str).str.replace("+7", "").str.replace(" ", "")
    df["phone"] = df["phone"].replace(["", "nan", "<NA>"], pd.NA)

    dupes = df[df.duplicated(subset=["email"], keep="first")]
    for _, row in dupes.iterrows():
        log_bad("customers", row["customer_id"], f"дубль email: {row['email']}")
    df = df.drop_duplicates(subset=["email"], keep="first")

    print(f"customers после очистки: {len(df)}")
    return df


def transform_orders(df):
    df = df.copy()
    df["order_timestamp"] = pd.to_datetime(df["order_timestamp"], format="mixed", errors="coerce")

    bad_dates = df[df["order_timestamp"].isna()]
    for _, row in bad_dates.iterrows():
        log_bad("orders", row["order_id"], "невалидная дата")
    df = df.dropna(subset=["order_timestamp"])

    bad_cust = df[df["customer_id"].isna()]
    for _, row in bad_cust.iterrows():
        log_bad("orders", row["order_id"], "пустой customer_id")
    df = df.dropna(subset=["customer_id"])
    df["customer_id"] = df["customer_id"].astype(int)

    bad_qty = df[df["quantity"] <= 0]
    for _, row in bad_qty.iterrows():
        log_bad("orders", row["order_id"], f"некорректное количество: {row['quantity']}")
    df = df[df["quantity"] > 0]

    df = df.drop_duplicates(subset=["order_id"], keep="first")

    print(f"orders после очистки: {len(df)}")
    return df


def transform_products(df):
    df = df.copy()
    df["product_name"] = df["product_name"].str.strip()
    df["category"] = df["category"].str.strip()
    df["is_active"] = df["is_active"].astype(bool)

    bad_price = df[df["price"] <= 0]
    for _, row in bad_price.iterrows():
        log_bad("products", row["product_id"], f"некорректная цена: {row['price']}")
    df = df[df["price"] > 0]

    dupes = df[df.duplicated(subset=["product_id"], keep="first")]
    for _, row in dupes.iterrows():
        log_bad("products", row["product_id"], f"дубль product_id")
    df = df.drop_duplicates(subset=["product_id"], keep="first")

    print(f"products после очистки: {len(df)}")
    return df


def transform_payments(df):
    df = df.copy()
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    bad_amount = df[df["amount"].isna()]
    for _, row in bad_amount.iterrows():
        log_bad("payments", row["payment_id"], "некорректная сумма (error_amount)")
    df = df.dropna(subset=["amount"])

    negative = df[df["amount"] <= 0]
    for _, row in negative.iterrows():
        log_bad("payments", row["payment_id"], f"сумма <= 0: {row['amount']}")
    df = df[df["amount"] > 0]

    df["payment_method"] = df["payment_method"].fillna("unknown")
    df["payment_timestamp"] = pd.to_datetime(df["payment_timestamp"], errors="coerce")

    df = df.drop_duplicates(subset=["payment_id"], keep="first")

    print(f"payments после очистки: {len(df)}")
    return df


def transform_events(df):
    df = df.copy()
    df["event_timestamp"] = pd.to_datetime(df["event_timestamp"], errors="coerce")

    bad_ts = df[df["event_timestamp"].isna()]
    for _, row in bad_ts.iterrows():
        log_bad("events", row["event_id"], "невалидный timestamp")
    df = df.dropna(subset=["event_timestamp"])

    bad_cust = df[df["customer_id"].isna()]
    for _, row in bad_cust.iterrows():
        log_bad("events", row["event_id"], "пустой customer_id")
    df = df.dropna(subset=["customer_id"])
    df["customer_id"] = df["customer_id"].astype(int)

    df = df.drop_duplicates(subset=["event_id"], keep="first")

    print(f"events после очистки: {len(df)}")
    return df


def transform_all(data):
    result = {
        "customers": transform_customers(data["customers"]),
        "orders": transform_orders(data["orders"]),
        "products": transform_products(data["products"]),
        "payments": transform_payments(data["payments"]),
        "events": transform_events(data["events"]),
    }
    save_log()
    return result