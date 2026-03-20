import pandas as pd


def recommend_product_placement(rows):

    # Convert rows to dataframe automatically
    df = pd.DataFrame(rows)

    # Rename only the columns we need
    df.columns = ["id","customer_id","door","shelf","dwell_time","purchase"]

    # Count shelf visits
    shelf_visits = df.groupby("shelf")["customer_id"].count()

    best_shelf = shelf_visits.idxmax()
    worst_shelf = shelf_visits.idxmin()

    print("\nAI Product Placement Suggestions")
    print("--------------------------------")

    print(f"High demand shelf → {best_shelf}")
    print("Place premium products here")

    print(f"Low traffic shelf → {worst_shelf}")
    print("Place discount items here")