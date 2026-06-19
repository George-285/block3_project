SELECT
    d.year,
    d.month,
    d.month_name,
    ROUND(SUM(o.total_amount)::NUMERIC, 2) AS revenue
FROM fact_orders o
JOIN dim_date d ON o.date_id = d.date_id
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;