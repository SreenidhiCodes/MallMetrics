import sqlite3

# ✅ USE SAME DB AS ENTIRE SYSTEM
DB_FILE = "database/mall.db"

# =========================================
# 🔥 INIT ZONE TABLE
# =========================================
def init_zone_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS zones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        zone_row INTEGER,
        zone_col INTEGER,
        dwell_time REAL,
        x INTEGER,
        y INTEGER
    )
    """)

    conn.commit()
    conn.close()


# =========================================
# 📥 INSERT ZONE DATA
# =========================================
def insert_zone(customer_id, zone_row, zone_col, dwell_time, x, y):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
        INSERT INTO zones 
        (customer_id, zone_row, zone_col, dwell_time, x, y)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (customer_id, zone_row, zone_col, dwell_time, x, y))

    conn.commit()
    conn.close()


# =========================================
# 📤 FETCH ZONE DATA (FOR DASHBOARD)
# =========================================
def fetch_zone_data():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    try:
        c.execute("""
            SELECT customer_id, zone_row, zone_col, dwell_time, x, y
            FROM zones
        """)
        rows = c.fetchall()
    except Exception as e:
        print("Error fetching zone data:", e)
        rows = []

    conn.close()
    return rows


# =========================================
# 🧹 OPTIONAL: CLEAR ZONE DATA
# =========================================
def clear_zone_data():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("DELETE FROM zones")

    conn.commit()
    conn.close()