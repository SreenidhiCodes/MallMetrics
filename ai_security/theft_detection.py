import pandas as pd

def detect_theft(rows):

    # -----------------------------
    # Create DataFrame
    # -----------------------------
    df = pd.DataFrame(rows, columns=[
        "id",
        "customer_id",
        "door",
        "shelf",
        "dwell_time",
        "purchase",
        "x",
        "y"
    ])

    if df.empty:
        print("\nNo data available")
        return

    # -----------------------------
    # Aggregate per customer
    # -----------------------------
    grouped = df.groupby("customer_id").agg({
        "door": "last",
        "shelf": lambda x: list(set(x)),
        "dwell_time": "max",
        "purchase": "max",
        "x": "last",
        "y": "last"
    }).reset_index()

    # -----------------------------
    # Suspicion Scoring System
    # -----------------------------
    suspects = []

    for _, row in grouped.iterrows():

        score = 0
        reasons = []

        # 1. Shelf interaction
        if "None" not in row["shelf"]:
            score += 2
            reasons.append("Interacted with shelf")

        # 2. No purchase
        if row["purchase"] == 0:
            score += 3
            reasons.append("No purchase")

        # 3. Long dwell time (realistic threshold)
        if row["dwell_time"] > 5:
            score += 2
            reasons.append("Long shelf time")

        # 4. Exit near door (possible leaving)
        if row["door"] in ["DoorA", "DoorB"]:
            score += 1
            reasons.append("Exited store")

        # 5. Optional movement-based suspicion (approx)
        if row["x"] < 150 or row["x"] > 1000:
            score += 1
            reasons.append("Near exit zone")

        # -----------------------------
        # Final Decision
        # -----------------------------
        if score >= 6:

            suspects.append({
                "customer_id": row["customer_id"],
                "score": score,
                "reasons": ", ".join(reasons)
            })

    # -----------------------------
    # Output
    # -----------------------------
    print("\n SECURITY ANALYSIS ")

    if suspects:

        print("\n⚠ HIGH RISK CUSTOMERS DETECTED:\n")

        for s in suspects:

            print(f"Customer {s['customer_id']}")
            print(f"Risk Score: {s['score']}")
            print(f"Reasons: {s['reasons']}")
            print("-" * 40)

    else:

        print("No suspicious activity detected")