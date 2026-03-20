import sqlite3
from collections import defaultdict, Counter

DB_FILE = "zone_data.db"

def zone_advanced_report():

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("SELECT zone_row, zone_col, dwell_time FROM zone_activity")
    data = c.fetchall()

    zone_visits = Counter()
    zone_dwell = defaultdict(list)

    for row, col, dwell in data:
        zone_visits[(row, col)] += 1
        zone_dwell[(row, col)].append(dwell)

    print("\n🗺️ ZONE POPULARITY:")
    for z, count in zone_visits.most_common():
        print(f"{z} → {count} visits")

    print("\n⏱️ ZONE DWELL TIME:")
    avg_dwell_zone = {}
    for z in zone_dwell:
        avg = sum(zone_dwell[z]) / len(zone_dwell[z])
        avg_dwell_zone[z] = avg
        print(f"{z} → {avg:.2f} sec")

    # 🔥 CROWD DENSITY
    print("\n👥 CROWD DENSITY HOTSPOTS:")
    for z, count in zone_visits.most_common(3):
        print(f"{z} → High traffic ({count})")

    # 🔥 THEFT RISK LOGIC
    print("\n🚨 RISK ZONES (SMART INSIGHT):")

    for z in zone_visits:
        visits = zone_visits[z]
        dwell = avg_dwell_zone[z]

        if visits > 50 and dwell < 2:
            print(f"{z} → ⚠️ High theft risk (crowded + quick movement)")

        elif visits < 10 and dwell > 5:
            print(f"{z} → ⚠️ Hidden zone risk (isolated area)")

    conn.close()