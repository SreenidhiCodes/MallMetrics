import sqlite3
import pandas as pd
from collections import Counter

DB_NAME = "retail_store.db"

# -----------------------------
# Load data from database
# -----------------------------
def load_customer_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM customer", conn)
    conn.close()
    return df

def load_brand_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM brand", conn)
    conn.close()
    return df

def load_shelf_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM shelf", conn)
    conn.close()
    return df

# -----------------------------
# Demand prediction functions
# -----------------------------
def brand_popularity():
    """Return the most popular brand based on customer purchase counts"""
    df = load_customer_data()
    if df.empty:
        print("No customer data found.")
        return
    
    brand_counts = df['brand_id'].value_counts()
    top_brand_id = brand_counts.idxmax()
    top_count = brand_counts.max()

    brand_df = load_brand_data()
    top_brand_name = brand_df[brand_df['brand_id']==top_brand_id]['brand_name'].values[0]
    print(f"Most popular brand: {top_brand_name} ({top_count} purchases)")

def shelf_demand():
    """Return average dwell time and total customers per shelf"""
    df = load_customer_data()
    if df.empty:
        print("No customer data found.")
        return

    shelf_df = load_shelf_data()
    grouped = df.groupby('shelf_id').agg(
        avg_dwell_time=('dwell_time', 'mean'),
        customer_count=('customer_id', 'nunique')
    ).reset_index()

    merged = grouped.merge(shelf_df, left_on='shelf_id', right_on='shelf_id')
    print("\nShelf demand analysis:")
    for idx, row in merged.iterrows():
        print(f"Shelf: {row['shelf_name']}, Avg Dwell Time: {row['avg_dwell_time']:.2f}s, Customers: {row['customer_count']}")

def demand_by_time(interval='hour'):
    """Optional: analyze demand by time intervals"""
    df = load_customer_data()
    if df.empty:
        print("No customer data found.")
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    if interval == 'hour':
        df['hour'] = df['timestamp'].dt.hour
        grouped = df.groupby('hour').agg(customer_count=('customer_id','nunique')).reset_index()
        print("\nCustomer count per hour:")
        print(grouped)
    elif interval == 'day':
        df['day'] = df['timestamp'].dt.date
        grouped = df.groupby('day').agg(customer_count=('customer_id','nunique')).reset_index()
        print("\nCustomer count per day:")
        print(grouped)

# -----------------------------
# Main function
# -----------------------------
if __name__ == "__main__":
    print("📊 Demand Prediction Analysis\n")
    brand_popularity()
    shelf_demand()
    demand_by_time(interval='hour')