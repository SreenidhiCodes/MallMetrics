import sqlite3

DB_FILE = "retail_data.db"

def store_behavior_analysis():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("SELECT AVG(dwell_time) FROM customer")
    avg_dwell = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM customer WHERE purchase=1")
    purchases = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM suspect")
    suspects = c.fetchone()[0]

    conn.close()
    print(f"📊 Avg Dwell Time: {avg_dwell:.2f}s")
    print(f"📊 Total Purchases: {purchases}")
    print(f"📊 Total Suspects: {suspects}")