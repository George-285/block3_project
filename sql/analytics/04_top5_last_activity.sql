SELECT
    c.customer_id,
    c.full_name,
    COUNT(o.order_id) AS total_orders,
    MAX(e.date_id) AS last_activity
FROM dim_customers c
JOIN fact_orders o ON c.customer_id = o.customer_id
LEFT JOIN fact_events e ON c.customer_id = e.customer_id
GROUP BY c.customer_id, c.full_name
ORDER BY total_orders DESC
LIMIT 5;