import pandas as pd

def optimize_layout(rows):

    df = pd.DataFrame(rows,columns=[
        "id","customer_id","door","shelf","dwell_time","purchase"
    ])

    popularity = df.groupby("shelf")["dwell_time"].mean()

    best = popularity.idxmax()

    print("\nBest Shelf Location:",best)