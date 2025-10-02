import psycopg2
import pandas as pd

# Connection data
DB_HOST = "localhost"
DB_NAME = "ecommerce"
DB_USER = "postgres"
DB_PASS = "Abla_sf65"
DB_PORT = 5432

# Path to the SQL file
SQL_FILE = "/Users/dariyaablanova/Desktop/unic_work/DataVis/Assignment/queries.sql"

# Creates and returns a connection to PostgreSQL.
def get_connection():
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
        print("Error connecting to the database:", e)
        return None

# Run SQL query and return DataFrame
def run_query(query):
    conn = get_connection()
    if not conn:
        return None
    try:
        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()

# Loads SQL queries into a dict {name: query}
def load_queries():
    queries = {}
    try:
        with open(SQL_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # Разбиваем по тегу -- name:
        parts = content.split("-- name:")
        for part in parts[1:]:
            lines = part.strip().splitlines()
            name = lines[0].strip()  # имя после -- name:
            sql = "\n".join(lines[1:]).strip()  
            queries[name] = sql
        return queries
    except Exception as e:
        print("Error loading SQL file:", e)
        return {}
    

# Example of connection test and query loading
if __name__ == "__main__":
    conn = get_connection()
    if conn:
        print("✅ Connection to the database established.")
        queries = load_queries()
        if queries:
            print(f"✅ Loaded {len(queries)} SQL queries: {list(queries.keys())[:3]}...")
        conn.close()
