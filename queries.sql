-- name: revenue_by_state
-- Получаем топ штатов по выручке и количеству заказов
SELECT 
    c.customer_state,
    COUNT(o.order_id) as total_orders,
    SUM(p.payment_value) as total_revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_payments p ON o.order_id = p.order_id
GROUP BY c.customer_state
ORDER BY total_revenue DESC
LIMIT 10;

-- name: sales_by_month_states
-- Суммарная выручка и количество заказов по месяцам для выбранных штатов
SELECT 
    c.customer_state,
    DATE_TRUNC('month', o.order_purchase_timestamp) as order_month,
    COUNT(o.order_id) as monthly_orders,
    SUM(p.payment_value) as monthly_revenue
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_payments p ON o.order_id = p.order_id
WHERE c.customer_state IN ('SP', 'RJ', 'MG', 'RS', 'PR')
GROUP BY c.customer_state, order_month
ORDER BY c.customer_state, order_month;

-- name: delivery_by_category
-- Среднее время доставки, количество заказов и выручка по категориям товаров
SELECT 
    p.product_category_name,
    COUNT(o.order_id) as total_orders,
    AVG(EXTRACT(day FROM (o.order_delivered_customer_date - o.order_purchase_timestamp))) as avg_delivery_days,
    SUM(oi.price) as total_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_delivered_customer_date IS NOT NULL
GROUP BY p.product_category_name
HAVING COUNT(o.order_id) >= 50
ORDER BY avg_delivery_days DESC;

-- name: top_sellers
-- Топ продавцов по выручке с количеством заказов и средней оценкой отзывов
SELECT 
    CONCAT(s.seller_city, ' (', s.seller_state, ')') as seller_location,
    COUNT(oi.order_id) as total_orders,
    SUM(oi.price) as total_revenue,
    AVG(r.review_score) as avg_review_score
FROM sellers s
JOIN order_items oi ON s.seller_id = oi.seller_id
JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN order_reviews r ON o.order_id = r.order_id
GROUP BY s.seller_city, s.seller_state
HAVING COUNT(oi.order_id) >= 50
ORDER BY total_revenue DESC
LIMIT 15;

-- name: active_cities
-- Топ городов по выручке с количеством заказов и средней оценкой удовлетворенности
-- Heatmap
SELECT 
    c.customer_city AS city,
    c.customer_state AS state,
    SUM(p.payment_value) AS total_revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_payments p ON o.order_id = p.order_id
GROUP BY c.customer_city, c.customer_state
HAVING SUM(p.payment_value) >= 10000
ORDER BY total_revenue DESC;

-- name: payment_methods
-- Количество транзакций, суммарная и средняя стоимость по способам оплаты
SELECT 
    op.payment_type,
    COUNT(*) as transaction_count,
    SUM(op.payment_value) as total_processed,
    AVG(op.payment_value) as avg_transaction_value
FROM order_payments op
JOIN orders o ON op.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY op.payment_type
ORDER BY total_processed DESC;

-- name: top_products
-- Топ товаров по выручке с количеством продаж, средней ценой и рейтингом
SELECT 
    p.product_id,
    p.product_category_name,
    COUNT(oi.order_id) as times_sold,
    SUM(oi.price) as total_revenue,
    AVG(oi.price) as avg_price,
    AVG(r.review_score) as avg_rating
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN order_reviews r ON o.order_id = r.order_id
GROUP BY p.product_id, p.product_category_name
HAVING COUNT(oi.order_id) >= 10
ORDER BY total_revenue DESC
LIMIT 20;

--Geo Visualization
SELECT 
    g.geolocation_lat AS lat,
    g.geolocation_lng AS lon,
    s.seller_id
FROM sellers s
JOIN geolocation g 
    ON s.seller_zip_code_prefix = g.geolocation_zip_code_prefix;


-- Sunburst chart
-- Product Category → Seller → Product
SELECT
    p.product_category_name AS category,
    s.seller_id AS seller,
    p.product_id AS product,
    SUM(oi.price) AS total_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN sellers s ON oi.seller_id = s.seller_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY p.product_category_name, s.seller_id, p.product_id
HAVING SUM(oi.price) >= 1000
ORDER BY total_revenue DESC;

-- Treemap chart
-- Product Category → Delivery Status → Total Orders
SELECT
    p.product_category_name AS category,
    o.order_status AS delivery_status,
    COUNT(o.order_id) AS total_orders
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_category_name, o.order_status
HAVING COUNT(o.order_id) >= 50
ORDER BY total_orders DESC;

-- Word Cloud
-- Frequently encountered categories
SELECT 
    p.product_category_name AS word,
    COUNT(oi.order_id) AS frequency
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY p.product_category_name
HAVING COUNT(oi.order_id) >= 20
ORDER BY frequency DESC;

--Data Engineering в Superset 
SELECT 
    DATE_TRUNC('month', order_purchase_timestamp::timestamp) AS order_month,
    COUNT(order_id) AS total_orders,
    'DB' AS source
FROM orders
GROUP BY order_month

UNION ALL

SELECT 
    DATE_TRUNC('month', order_purchase_timestamp::timestamp) AS order_month,
    COUNT(order_id) AS total_orders,
    'CSV' AS source
FROM orders_csv
GROUP BY order_month
ORDER BY order_month;


-- name: order_status_delivery
-- Среднее время доставки и количество заказов по статусу заказа
SELECT 
    o.order_status,
    COUNT(*) as order_count,
    AVG(EXTRACT(day FROM (o.order_delivered_customer_date - o.order_purchase_timestamp))) as avg_delivery_days
FROM orders o
WHERE o.order_delivered_customer_date IS NOT NULL
GROUP BY o.order_status
ORDER BY order_count DESC;

-- name: price_freight_by_category
-- Средняя цена, средняя доставка, суммарная выручка и продажи по категориям товаров
SELECT 
    p.product_category_name,
    AVG(oi.price) as avg_price,
    AVG(oi.freight_value) as avg_freight,
    SUM(oi.price) as total_revenue,
    COUNT(oi.order_id) as total_sales
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY p.product_category_name
HAVING COUNT(oi.order_id) >= 100
ORDER BY total_revenue DESC;

-- name: reviews_by_category
-- Количество и рейтинг отзывов по категориям товаров, включая 5-звёздочные и низкие оценки
SELECT 
    p.product_category_name,
    COUNT(r.review_id) as review_count,
    AVG(r.review_score) as avg_score,
    COUNT(CASE WHEN r.review_score = 5 THEN 1 END) as five_star_reviews,
    COUNT(CASE WHEN r.review_score <= 2 THEN 1 END) as low_reviews
FROM order_reviews r
JOIN orders o ON r.order_id = o.order_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_category_name
HAVING COUNT(r.review_id) >= 50
ORDER BY avg_score DESC;
