SELECT
    c.customer_id,
    c.full_name,
    ROUND(SUM(o.total_amount)::NUMERIC, 2) AS total_spent
FROM fact_orders o
JOIN dim_customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.full_name
ORDER BY total_spent DESC
LIMIT 10;