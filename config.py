import psycopg2
import time
import random
from datetime import datetime, timedelta
import uuid

# Connection data
DB_HOST = "localhost"
DB_NAME = "ecommerce"
DB_USER = "postgres"
DB_PASS = "Abla_sf65"
DB_PORT = 5432

# Интервал обновления (в секундах)
INTERVAL = 5 

def get_connection():
    """Создает и возвращает подключение к PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return None

def get_random_ids(conn):
    cursor = conn.cursor()
    ids = {}
    
    try:
        # Получаем существующие customer_id
        cursor.execute("SELECT customer_id FROM customers ORDER BY RANDOM() LIMIT 100;")
        ids['customers'] = [row[0] for row in cursor.fetchall()]
        
        # Получаем существующие product_id и seller_id
        cursor.execute("SELECT product_id FROM products ORDER BY RANDOM() LIMIT 100;")
        ids['products'] = [row[0] for row in cursor.fetchall()]
        
        # Получаем существующие seller_id
        cursor.execute("SELECT seller_id FROM sellers ORDER BY RANDOM() LIMIT 50;")
        ids['sellers'] = [row[0] for row in cursor.fetchall()]
        
        print(f"✅ Загружено: {len(ids['customers'])} покупателей, {len(ids['products'])} товаров, {len(ids['sellers'])} продавцов")
        
    except Exception as e:
        print(f"❌ Ошибка при получении ID: {e}")
    finally:
        cursor.close()
    
    return ids

def generate_order_id():
    """Генерирует уникальный order_id"""
    return str(uuid.uuid4())[:32]  # character varying, обрезаем до разумной длины

def insert_order_with_items(conn, ids):
    """Вставляет новый заказ и его позиции"""
    cursor = conn.cursor()
    
    try:
        # Генерируем данные для заказа
        order_id = generate_order_id()
        customer_id = random.choice(ids['customers'])
        
        # Статусы заказов
        statuses = ['delivered', 'shipped', 'processing', 'approved', 'invoiced']
        order_status = random.choice(statuses)
        
        # Временные метки
        purchase_time = datetime.now() - timedelta(days=random.randint(0, 30))
        approved_at = purchase_time + timedelta(hours=random.randint(1, 48)) if order_status != 'processing' else None
        delivered_date = approved_at + timedelta(days=random.randint(3, 15)) if order_status == 'delivered' else None
        estimated_delivery = purchase_time + timedelta(days=random.randint(7, 30))
        
        # Вставляем заказ
        order_query = """
        INSERT INTO orders (
            order_id, customer_id, order_status, 
            order_purchase_timestamp, order_approved_at, 
            order_delivered_customer_date, order_estimated_delivery_date
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(order_query, (
            order_id, customer_id, order_status,
            purchase_time, approved_at, delivered_date, estimated_delivery
        ))
        
        # Добавляем 1-3 позиции в заказ
        num_items = random.randint(1, 3)
        total_order_value = 0
        
        for item_num in range(1, num_items + 1):
            product_id = random.choice(ids['products'])
            seller_id = random.choice(ids['sellers'])
            
            # Генерируем реалистичную цену в зависимости от категории
            # Получаем категорию товара для более реалистичных цен
            cursor.execute("""
                SELECT product_category_name 
                FROM products WHERE product_id = %s;
            """, (product_id,))
            result = cursor.fetchone()
            category = result[0] if result else None
            
            # Разные диапазоны цен для разных категорий
            if category and 'eletronicos' in str(category).lower():
                price = round(random.uniform(100.0, 2000.0), 2)  # Электроника дороже
            elif category and 'moveis' in str(category).lower():
                price = round(random.uniform(200.0, 1500.0), 2)  # Мебель
            else:
                price = round(random.uniform(10.0, 500.0), 2)  # Остальное
            
            freight_value = round(random.uniform(5.0, 50.0), 2)
            shipping_limit = purchase_time + timedelta(days=random.randint(1, 5))
            
            item_query = """
            INSERT INTO order_items (
                order_id, order_item_id, product_id, seller_id,
                shipping_limit_date, price, freight_value
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(item_query, (
                order_id, item_num, product_id, seller_id,
                shipping_limit, price, freight_value
            ))
            
            # Добавляем к общей сумме заказа
            total_order_value += price + freight_value
        
        # Добавляем платеж
        payment_types = ['credit_card', 'boleto', 'voucher', 'debit_card']
        payment_type = random.choice(payment_types)
        payment_installments = random.randint(1, 12) if payment_type == 'credit_card' else 1
        
        payment_query = """
        INSERT INTO order_payments (
            order_id, payment_sequential, payment_type, 
            payment_installments, payment_value
        )
        VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(payment_query, (
            order_id, 1, payment_type, payment_installments, total_order_value
        ))
        
        conn.commit()
        
        print(f"✅ Заказ создан: {order_id[:12]}...")
        print(f"   Покупатель: {customer_id}")
        print(f"   Статус: {order_status}")
        print(f"   Позиций: {num_items}, Сумма: ${total_order_value:.2f}")
        print(f"   Дата: {purchase_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Ошибка при создании заказа: {e}")
        conn.rollback()
    finally:
        cursor.close()

def insert_review(conn, ids):
    cursor = conn.cursor()
    
    try:
        # Получаем случайный существующий order_id
        cursor.execute("""
            SELECT order_id FROM orders 
            WHERE order_status = 'delivered' 
            ORDER BY RANDOM() LIMIT 1;
        """)
        result = cursor.fetchone()
        
        if not result:
            print("⚠️  Нет доставленных заказов для отзыва")
            return
        
        order_id = result[0]
        review_id = str(uuid.uuid4())[:32]
        review_score = random.randint(1, 5)
        
        # Генерируем комментарий в зависимости от оценки
        positive_comments = [
            "Excellent product! Fast delivery",
            "Very satisfied with the purchase",
            "Great quality, highly recommend",
            "Perfect! Exactly what I needed"
        ]
        
        negative_comments = [
            "Delivery was delayed",
            "Product quality could be better",
            "Not exactly as described",
            "Average experience"
        ]
        
        comment_title = random.choice(positive_comments if review_score >= 4 else negative_comments)
        comment_message = "Thank you!" if review_score >= 4 else "Could be improved"
        
        creation_date = datetime.now()
        answer_timestamp = creation_date + timedelta(days=random.randint(1, 3))
        
        review_query = """
        INSERT INTO order_reviews (
            review_id, order_id, review_score, 
            review_comment_title, review_comment_message,
            review_creation_date, review_answer_timestamp
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(review_query, (
            review_id, order_id, review_score,
            comment_title, comment_message,
            creation_date, answer_timestamp
        ))
        
        conn.commit()
        
        print(f"✅ Отзыв добавлен: {'⭐' * review_score} ({review_score}/5)")
        print(f"   '{comment_title}'")
        
    except Exception as e:
        print(f"❌ Ошибка при добавлении отзыва: {e}")
        conn.rollback()
    finally:
        cursor.close()

def main():
    """Основная функция"""
    print("🚀 Запуск скрипта автоматического добавления данных в БД 'ecommerce'...")
    print(f"⏱️  Интервал обновления: {INTERVAL} секунд")
    print("⏹️  Для остановки нажмите Ctrl+C\n")
    
    conn = get_connection()
    if not conn:
        return
    
    # Получаем существующие ID из таблиц
    ids = get_random_ids(conn)
    if not ids['customers'] or not ids['products']:
        print("❌ Не удалось загрузить ID. Проверьте таблицы.")
        conn.close()
        return
    
    try:
        iteration = 1
        while True:
            print(f"\n{'='*70}")
            print(f"📊 Итерация #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*70}")
            
            # Добавляем новый заказ с позициями
            insert_order_with_items(conn, ids)
            
            # С вероятностью 20% добавляем отзыв на существующий заказ
            if random.random() < 0.2:
                time.sleep(2)
                insert_review(conn, ids)
            
            iteration += 1
            print(f"\n⏳ Ожидание {INTERVAL} секунд до следующей вставки...")
            time.sleep(INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Скрипт остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Непредвиденная ошибка: {e}")
    finally:
        if conn:
            conn.close()
            print("🔌 Соединение с БД закрыто")

if __name__ == "__main__":
    main()