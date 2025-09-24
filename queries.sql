-- 1. Посмотреть первые 10 покупателей
SELECT *
FROM customers c
LIMIT 10;

-- 2. Найти все заказы из штата SP и отсортировать по дате покупки
SELECT o.order_id, c.customer_id, o.order_purchase_timestamp
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_state = 'SP'
ORDER BY o.order_purchase_timestamp DESC;

-- 3. Посчитать количество заказов по статусам
SELECT o.order_status, COUNT(*) AS total_orders
FROM orders o
GROUP BY o.order_status
ORDER BY total_orders DESC;

-- 4. Среднее, минимальное и максимальное время доставки (разница между датой получения и покупки)
SELECT 
    AVG(o.order_delivered_customer_date - o.order_purchase_timestamp) AS avg_delivery_time,
    MIN(o.order_delivered_customer_date - o.order_purchase_timestamp) AS min_delivery_time,
    MAX(o.order_delivered_customer_date - o.order_purchase_timestamp) AS max_delivery_time
FROM orders o
WHERE o.order_delivered_customer_date IS NOT NULL;

-- 5. Средняя цена и стоимость доставки по категориям товаров
SELECT p.product_category_name,
       AVG(oi.price) AS avg_price,
       AVG(oi.freight_value) AS avg_freight
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY avg_price DESC;

-- 6. ТОП-10 продавцов по количеству проданных товаров
SELECT s.seller_id, s.seller_city, COUNT(*) AS total_sold
FROM order_items oi
JOIN sellers s ON oi.seller_id = s.seller_id
GROUP BY s.seller_id, s.seller_city
ORDER BY total_sold DESC
LIMIT 10;

-- 7. Количество заказов по городам покупателей
SELECT c.customer_city, COUNT(o.order_id) AS total_orders
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_city
ORDER BY total_orders DESC
LIMIT 10;

-- 8. Средняя оценка по отзывам для каждой категории товара
SELECT p.product_category_name, AVG(r.review_score) AS avg_score
FROM order_reviews r
JOIN orders o ON r.order_id = o.order_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY avg_score DESC;

-- 9. Количество заказов и сумма оплат по типу платежа
SELECT op.payment_type,
       COUNT(*) AS total_payments,
       SUM(op.payment_value) AS total_value
FROM order_payments op
GROUP BY op.payment_type
ORDER BY total_value DESC;

-- 10. ТОП-5 самых прибыльных товаров (по общей выручке)
SELECT oi.product_id, p.product_category_name, SUM(oi.price) AS total_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY oi.product_id, p.product_category_name
ORDER BY total_revenue DESC
LIMIT 5;
