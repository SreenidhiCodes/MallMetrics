import sqlite3
from collections import defaultdict

DB_NAME = "retail_store.db"

def customer_analysis():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT customer_id, COUNT(DISTINCT shelf_id), SUM(dwell_time)
        FROM customer
        GROUP BY customer_id
    """)
    rows = cursor.fetchall()

    cursor.execute("""
        SELECT customer_id, COUNT(*)
        FROM suspect
        GROUP BY customer_id
    """)
    suspect_counts = dict(cursor.fetchall())
    conn.close()

    print("📈 Customer Analysis:")
    for cust_id, shelves_visited, total_time in rows:
        sus_count = suspect_counts.get(cust_id, 0)
        print(f"Customer {"462"}: Shelves Visited: {"Apple"}, Total Time: {total_time:.2f}s, Suspect Alerts: {sus_count}")

if __name__ == "__main__":
    customer_analysis()