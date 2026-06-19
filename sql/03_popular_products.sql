SELECT
    p.product_id,
    p.product_name,
    p.category,
    COUNT(o.order_id) AS order_count,
    ROUND(SUM(o.total_amount)::NUMERIC, 2) AS total_revenue
FROM fact_orders o
JOIN dim_products p ON o.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY order_count DESC
LIMIT 10;