import pandas as pd
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data"


def extract_customers():
    df = pd.read_csv(DATA_DIR / "customers.csv", encoding="utf-8")
    print(f"customers: {len(df)} строк")
    return df


def extract_orders():
    df = pd.read_json(DATA_DIR / "orders.json")
    print(f"orders: {len(df)} строк")
    return df


def extract_products():
    df = pd.read_excel(DATA_DIR / "products.xlsx", engine="openpyxl")
    print(f"products: {len(df)} строк")
    return df


def extract_payments():
    df = pd.read_csv(DATA_DIR / "payments.csv", sep="^")
    print(f"payments: {len(df)} строк")
    return df


def extract_events():
    df = pd.read_xml(DATA_DIR / "events.xml")
    print(f"events: {len(df)} строк")
    return df


def extract_all():
    data = {
        "customers": extract_customers(),
        "orders": extract_orders(),
        "products": extract_products(),
        "payments": extract_payments(),
        "events": extract_events(),
    }
    print(f"\nвсего загружено {len(data)} источников")
    return data


if __name__ == "__main__":
    result = extract_all()
    for name, df in result.items():
        print(f"\n{name}:")
        print(df.head(3))