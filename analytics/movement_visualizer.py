import matplotlib.pyplot as plt
import sqlite3

DB_FILE = "retail_data.db"

def customer_behavior():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT customer_id, cx, cy FROM customer")
    rows = c.fetchall()
    conn.close()

    if not rows:
        print("⚠️ No movement data found")
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    unique_customers = list(set(r[0] for r in rows))

    for cid in unique_customers:
        path = [(r[1], r[2]) for r in rows if r[0] == cid]
        if len(path) > 1:
            x, y = zip(*path)
            ax.plot(x, y, linewidth=1, alpha=0.6)

    ax.set_title("Customer Movement Patterns", fontsize=16, fontweight='bold')
    ax.set_xlabel("Store Width")
    ax.set_ylabel("Store Height")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()