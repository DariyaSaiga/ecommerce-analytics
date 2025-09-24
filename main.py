import psycopg2
import pandas as pd

# Параметры подключения к базе
DB_HOST = "localhost"
DB_NAME = "ecommerce"
DB_USER = "postgres"
DB_PASS = "Abla_sf65" 
DB_PORT = 5432

# Файл с SQL-запросами
SQL_FILE = "/Users/dariyaablanova/Desktop/unic_work/DataVis/Assignment1/queries.sql"

# Список SQL-запросов для выполнения
def main():
    try:
        # Подключение к базе
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        cursor = conn.cursor()
        print("✅ Подключение к базе успешно!")

        # Читаем весь файл queries.sql
        with open(SQL_FILE, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # Разделяем на отдельные запросы по ;
        sql_statements = [s.strip() for s in sql_content.split(';') if s.strip()]

        for i, query in enumerate(sql_statements, start=1):
            print(f"\n📌 Выполняем запрос #{i}")
            cursor.execute(query)
            rows = cursor.fetchall()

            # Выводим в терминал
            for row in rows:
                print(row)

            # Сохраняем в CSV
            df = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])
            df.to_csv(f"query_{i}.csv", index=False)
            print(f"💾 Результат сохранен в query_{i}.csv")

        cursor.close()
        conn.close()
        print("\n✅ Все запросы выполнены, соединение закрыто!")

    except Exception as e:
        print("❌ Ошибка:", e)

main()