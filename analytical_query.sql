SELECT 
    p.product_category_name AS categoria,
    c.customer_state AS stato_cliente,
    COUNT(o.order_id) AS totale_ordini,
    ROUND(SUM(o.price), 2) AS fatturato_totale
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_unique_id = c.customer_unique_id
GROUP BY categoria, stato_cliente
HAVING fatturato_totale > 100
ORDER BY fatturato_totale DESC;