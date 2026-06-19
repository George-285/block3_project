# ETL-пайплайн: Block 3

## Описание

End-to-end ETL-пайплайн для загрузки, очистки и аналитики данных из пяти источников разных форматов (CSV, JSON, XLSX, XML). Данные загружаются в PostgreSQL, моделируются по Star Schema и анализируются SQL-запросами.

## Стек

- Python 3.13
- pandas, openpyxl, lxml
- SQLAlchemy, psycopg2
- PostgreSQL

## Структура проекта
```
block3_project/
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── main.py
├── sql/
│   ├── 01_top10_customers.sql
│   ├── 02_revenue_by_month.sql
│   ├── 03_popular_products.sql
│   ├── 04_top5_last_activity.sql
│   └── 05_users_without_orders.sql
├── ddl/
│   └── 01_dwh.sql
├── data/
├── logs/
│   └── bad_records.csv
├── .gitignore
├── requirements.txt
└── README.md
```
## Как запустить

1. Установить зависимости:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

2. Создать базу данных в PostgreSQL:
CREATE DATABASE mosmusic_block3;

3. Выполнить DDL из `sql/ddl/01_dwh.sql` в DBeaver.
4. Заполнить `.env`:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mosmusic_block3
DB_USER=postgres
DB_PASSWORD=your_password

5. Запустить пайплайн:
cd src
python main.py

## Архитектура

Пайплайн состоит из трёх этапов:

**Extract:** чтение данных из 5 источников. Особенности: payments.csv использует разделитель `^`, products.xlsx содержит булевы значения в русской локали (ИСТИНА/ЛОЖЬ), events хранятся в XML.

**Transform:** очистка и валидация. Все проблемные записи логируются в `logs/bad_records.csv`. Применяются следующие правила:

- Удаление дубликатов по первичным ключам во всех таблицах
- Удаление записей с невалидными датами (например, 2025-99-99)
- Удаление записей с некорректными суммами (error_amount)
- Замена UNKNOWN и пустых значений в phone на NULL
- Нормализация телефонов (удаление +7)
- Приведение email к нижнему регистру
- Дедупликация customers по email (оставляем первую запись)
- Замена пустых payment_method на "unknown"

**Load:** двухслойная загрузка. Сначала данные загружаются в staging-таблицы (stg_*), затем перекладываются в DWH по модели Star Schema.

## DWH-модель (Star Schema)

Измерения (справочники):
- `dim_customers` — клиенты
- `dim_products` — товары
- `dim_date` — календарь дат

Факты (транзакции):
- `fact_orders` — заказы (с вычисляемым total_amount = quantity * unit_price)
- `fact_payments` — платежи
- `fact_events` — пользовательские события

Внешние ключи (FK) между фактами и измерениями убраны, так как в исходных данных присутствуют сиротские ссылки (product_id > 600 при максимуме 600 в products, customer_id = 999999 в events). Решено сохранить такие записи для полноты аналитики.

## Принятые решения по Data Quality

| Проблема | Решение | Обоснование |
|----------|---------|-------------|
| Дубли по первичным ключам | Удаление, keep=first | Вторые записи идентичны первым |
| Невалидные даты (2025-99-99) | Удаление | Невозможно восстановить корректную дату |
| error_amount в payments | Удаление | Нет числового значения для анализа |
| UNKNOWN в phone | Замена на NULL | Информативнее, чем текстовая заглушка |
| Пустой payment_method | Замена на "unknown" | Сохраняем запись для финансовой аналитики |
| Сиротские FK (product_id > 600) | Сохранение без FK-ограничений | Удаление 7-11% записей исказит аналитику |
| Дубли email у customers | Удаление, keep=first | Один аккаунт на email |

Всего отсеяно 228 записей из 5058 исходных (4.5%).

## Как воспроизвести результат

1. Положить 5 файлов данных в папку `data/`
2. Создать базу и выполнить DDL
3. Настроить `.env`
4. Запустить `python src/main.py`
5. Выполнить запросы из `sql/analytics/` в DBeaver