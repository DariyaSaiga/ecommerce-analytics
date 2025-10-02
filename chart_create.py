import matplotlib.pyplot as plt
import os
from config import run_query, load_queries

# Создаём папку для графиков
os.makedirs("charts", exist_ok=True)

queries = load_queries()

# 1. Horizontal bar chart — Revenue by state
def horizontal_bar_chart_revenue_by_state():
    df = run_query(queries["revenue_by_state"])
    print(f"[Horizontal Bar Chart] Rows: {len(df)} — Топ штатов по выручке")
    
    df = df.sort_values("total_revenue", ascending=True)
    
    plt.figure(figsize=(10,6))
    plt.barh(df["customer_state"], df["total_revenue"], color='skyblue')
    plt.xlabel("Revenue")
    plt.ylabel("State")
    plt.title("Top States by Revenue")
    plt.tight_layout()
    plt.savefig("charts/barh_revenue_by_state.png")
    plt.close()

# 2. Line chart — Sales by month for selected states
def line_chart_sales_by_month():
    df = run_query(queries["sales_by_month_states"])
    df["order_month"] = df["order_month"].dt.strftime("%Y-%m")
    print(f"[Line Chart] Rows: {len(df)} — Месячная выручка по штатам")
    
    plt.figure(figsize=(12,6))
    for state in df["customer_state"].unique():
        subset = df[df["customer_state"] == state]
        plt.plot(subset["order_month"], subset["monthly_revenue"], marker='o', label=state)
    
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.title("Monthly Revenue by State")
    plt.xticks(rotation=45)
    plt.legend(title="State")
    plt.tight_layout()
    plt.savefig("charts/line_sales_by_month.png")
    plt.close()

# 3. Bar chart — Payment methods
def bar_chart_payment_methods():
    df = run_query(queries["payment_methods"])
    print(f"[Bar Chart] Rows: {len(df)} — Количество транзакций по типам оплаты")
    
    plt.figure(figsize=(8,6))
    plt.bar(df["payment_type"], df["transaction_count"], color='orange')
    plt.xlabel("Payment Type")
    plt.ylabel("Number of Transactions")
    plt.title("Transactions by Payment Method")
    plt.tight_layout()
    plt.savefig("charts/bar_payment_methods.png")
    plt.close()

# 4. Histogram — Delivery by category
def histogram_delivery_by_category():
    df = run_query(queries["delivery_by_category"])
    
    # Убираем строки с пустыми категориями
    df = df[df["product_category_name"].notna()]
    df["product_category_name"] = df["product_category_name"].astype(str)
    
    print(f"[Histogram] Rows: {len(df)} — Среднее время доставки по категориям")
    
    plt.figure(figsize=(12,6))
    plt.bar(df["product_category_name"], df["avg_delivery_days"], color='green')
    plt.xlabel("Product Category")
    plt.ylabel("Average Delivery Days")
    plt.title("Average Delivery Time by Category")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("charts/hist_delivery_by_category.png")
    plt.close()

# 5. Pie chart — Reviews by category
def pie_chart_reviews_by_category():
    df = run_query(queries["reviews_by_category"])
    df = df.sort_values("five_star_reviews", ascending=False).head(10)
    print(f"[Pie Chart] Rows: {len(df)} — Доля 5-звёздочных отзывов по топ-10 категориям")
    
    plt.figure(figsize=(8,8))
    plt.pie(df["five_star_reviews"], labels=df["product_category_name"], autopct='%1.1f%%')
    plt.title("Proportion of Five-Star Reviews by Top Categories")
    plt.tight_layout()
    plt.savefig("charts/pie_reviews_by_category.png")
    plt.close()

# 6. Scatter plot — Top products
def scatter_top_products():
    df = run_query(queries["top_products"])
    print(f"[Scatter Plot] Rows: {len(df)} — Доход vs Продажи топ-продуктов (размер = рейтинг)")
    
    plt.figure(figsize=(10,6))
    plt.scatter(df["times_sold"], df["total_revenue"], s=df["avg_rating"]*50, c='purple', alpha=0.6)
    plt.xlabel("Times Sold")
    plt.ylabel("Total Revenue")
    plt.title("Top Products: Revenue vs Times Sold")
    plt.tight_layout()
    plt.savefig("charts/scatter_top_products.png")
    plt.close()

if __name__ == "__main__":
    horizontal_bar_chart_revenue_by_state()
    line_chart_sales_by_month()
    bar_chart_payment_methods()
    histogram_delivery_by_category()
    pie_chart_reviews_by_category()
    scatter_top_products()

