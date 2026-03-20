import sqlite3
from collections import Counter

DB_FILE = "retail_data.db"

def brand_popularity_chart():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT brand FROM customer")
    brands = [b[0] for b in c.fetchall()]
    conn.close()

    if not brands:
        print("⚠️ No brand data found")
        return

    counts = Counter(brands)
    for brand, count in counts.most_common():
        print(f"🏆 {brand}: {count}")