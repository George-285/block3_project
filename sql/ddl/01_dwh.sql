DROP TABLE IF EXISTS fact_events, fact_payments, fact_orders, dim_customers, dim_products, dim_date CASCADE;

CREATE TABLE dim_customers (
    customer_id INT PRIMARY KEY,
    full_name TEXT,
    email TEXT,
    phone TEXT,
    city TEXT,
    created_at TIMESTAMP
);

CREATE TABLE dim_products (
    product_id INT PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    price NUMERIC,
    currency TEXT,
    is_active BOOLEAN
);

CREATE TABLE dim_date (
    date_id DATE PRIMARY KEY,
    day INT,
    month INT,
    year INT,
    weekday INT,
    month_name TEXT
);

CREATE TABLE fact_orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    product_id INT,
    date_id DATE,
    quantity INT,
    unit_price NUMERIC,
    total_amount NUMERIC,
    currency TEXT,
    status TEXT
);

CREATE TABLE fact_payments (
    payment_id INT PRIMARY KEY,
    order_id INT,
    date_id DATE,
    payment_method TEXT,
    amount NUMERIC,
    currency TEXT
);

CREATE TABLE fact_events (
    event_id INT PRIMARY KEY,
    customer_id INT,
    product_id INT,
    date_id DATE,
    event_type TEXT
);