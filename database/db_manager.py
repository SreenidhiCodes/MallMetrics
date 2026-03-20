import sqlite3

DB_FILE = "retail_data.db"

# -------------------------------
# INIT DATABASE
# -------------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Clean start
    c.execute("DROP TABLE IF EXISTS customer")
    c.execute("DROP TABLE IF EXISTS suspect")

    # -------------------------------
    # CUSTOMER TABLE
    # -------------------------------
    c.execute("""
    CREATE TABLE customer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        door TEXT,
        shelf TEXT,
        brand TEXT,
        dwell_time REAL,
        purchase INTEGER,
        cx INTEGER,
        cy INTEGER
    )
    """)

    # -------------------------------
    # SUSPECT TABLE
    # -------------------------------
    c.execute("""
    CREATE TABLE suspect (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        shelf TEXT,
        brand TEXT,
        suspect_type TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Database Initialized")


# -------------------------------
# INSERT CUSTOMER
# -------------------------------
def insert_customer(customer_id, shelf, brand, door, purchase, dwell_time, cx, cy):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
        INSERT INTO customer (customer_id, shelf, brand, door, purchase, dwell_time, cx, cy)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (customer_id, shelf, brand, door, purchase, dwell_time, cx, cy))

    conn.commit()
    conn.close()


# -------------------------------
# INSERT SUSPECT (NO DUPLICATES)
# -------------------------------
def insert_suspect(customer_id, shelf, brand, suspect_type):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Avoid duplicate suspects
    c.execute("SELECT * FROM suspect WHERE customer_id=?", (customer_id,))
    if not c.fetchone():
        c.execute("""
            INSERT INTO suspect (customer_id, shelf, brand, suspect_type)
            VALUES (?, ?, ?, ?)
        """, (customer_id, shelf, brand, suspect_type))

    conn.commit()
    conn.close()

# -------------------------------
# FETCH DATA FOR DASHBOARD
# -------------------------------
def fetch_data():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
        SELECT 
            id,
            customer_id,
            door,
            shelf,
            dwell_time,
            purchase,
            cx as x,
            cy as y
        FROM customer
    """)

    rows = c.fetchall()

    conn.close()
    return rows

import sqlite3

def fetch_suspects():
    conn = sqlite3.connect("retail_data.db")
    c = conn.cursor()
    c.execute("SELECT customer_id, shelf, brand FROM suspect")
    data = c.fetchall()
    conn.close()
    return data