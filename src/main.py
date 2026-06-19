from extract import extract_all
from transform import transform_all
from load import load_to_staging, load_to_dwh


def main():
    raw = extract_all()
    clean = transform_all(raw)
    load_to_staging(clean)
    load_to_dwh(clean)


if __name__ == "__main__":
    main()