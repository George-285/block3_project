SELECT
    c.customer_id,
    c.full_name,
    c.email,
    c.created_at
FROM dim_customers c
LEFT JOIN fact_orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL
ORDER BY c.created_at DESC;


-- SELECT COUNT(DISTINCT customer_id) FROM fact_orders;

SELECT COUNT(*) FROM dim_customers c
LEFT JOIN fact_orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;