import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def generate_shelf_heatmap(rows):

    df = pd.DataFrame(rows, columns=[
        "id","customer_id","door","shelf","dwell_time","purchase","x","y"
    ])

    pivot = df.pivot_table(
        values="dwell_time",
        index="shelf",
        columns="door",
        aggfunc="sum"
    )

    plt.figure(figsize=(8,5))

    sns.heatmap(
        pivot,
        annot=True,
        fmt=".0f",
        cmap="YlOrRd",
        linewidths=1,
        linecolor='white'
    )

    plt.title("Shelf Traffic Heatmap", fontsize=14)

    return plt