import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from database.db_manager import fetch_data, fetch_suspects
from analytics.heatmap_generator import generate_shelf_heatmap
from database.zone_db import fetch_zone_data

# ---------------- CONFIG ----------------
st.set_page_config(page_title="MallMetrics AI", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.card {
    padding: 20px;
    border-radius: 15px;
    background: #f5f7fa;
    transition: 0.3s;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
.card:hover {
    transform: scale(1.05);
}
.title {
    font-size: 22px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("# 🛍️ MallMetrics AI")
st.markdown("### 🚀 Measure The Mall - Master The Market")

# ---------------- MODE CARDS ----------------
c1, c2 = st.columns(2)

with c1:
    st.markdown("""
    <div class="card">
    <div class="title">🟢 Mode 1: Shelf Intelligence</div>
    <br>
    ✔ Shelf heatmaps<br>
    ✔ Customer tracking<br>
    ✔ Suspect detection<br>
    ✔ KPI analytics
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="card">
    <div class="title">🔵 Mode 2: Zone Intelligence</div>
    <br>
    ✔ Grid-based tracking<br>
    ✔ Dwell heat zones<br>
    ✔ Risk detection<br>
    ✔ Works for any store
    </div>
    """, unsafe_allow_html=True)

mode = st.radio("Select Mode", ["Mode 1", "Mode 2"])

# =========================================================
# 🟢 MODE 1
# =========================================================
if mode == "Mode 1":

    rows = fetch_data()
    suspect_rows = fetch_suspects()

    df = pd.DataFrame(rows, columns=[
        "id","customer_id","door","shelf","dwell_time","purchase","x","y"
    ])

    sus_df = pd.DataFrame(suspect_rows, columns=[
        "Customer ID", "Shelf", "Brand"
    ])

    if df.empty:
        st.warning("No data available. Run video analyzer first.")
        st.stop()

    # CLEAN
    df["shelf"] = df["shelf"].astype(str).str.strip().str.title()
    df["door"] = df["door"].astype(str).str.strip()

    # FILTERS
    st.sidebar.header("🔍 Filters")

    door_filter = st.sidebar.multiselect(
        "🚪 Door", df["door"].unique(), df["door"].unique()
    )
    shelf_filter = st.sidebar.multiselect(
        "🗂️ Shelf", df["shelf"].unique(), df["shelf"].unique()
    )

    filtered_df = df[
        df["door"].isin(door_filter) &
        df["shelf"].isin(shelf_filter)
    ]

    # KPIs
    st.subheader("📊 Store Overview")

    c1, c2, c3 = st.columns(3)

    footfall = filtered_df["customer_id"].nunique()
    sales = filtered_df["purchase"].sum()
    conversion = (sales / footfall * 100) if footfall > 0 else 0

    c1.metric("👥 Footfall", footfall)
    c2.metric("💰 Sales", int(sales))
    c3.metric("📈 Conversion %", round(conversion,1))

    # DOOR ANALYSIS
    st.subheader("🚪 Door-wise Analysis")

    if not filtered_df.empty:

        door_perf = filtered_df.groupby("door").agg({
            "customer_id": "nunique",
            "purchase": "sum"
        }).reset_index()

        door_perf["conversion_rate"] = (
            door_perf["purchase"] / door_perf["customer_id"] * 100
        ).round(1)

        colors = ["#1f77b4", "#aec7e8"]
        bar_colors = [colors[i % 2] for i in range(len(door_perf))]

        fig1 = go.Figure()

        fig1.add_trace(go.Bar(
            x=door_perf["door"],
            y=door_perf["customer_id"],
            text=door_perf["customer_id"],
            textposition='auto',
            marker_color=bar_colors
        ))

        fig1.update_layout(title="Footfall per Door")
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.line(
            door_perf,
            x="door",
            y="conversion_rate",
            markers=True,
            title="Conversion Rate per Door (%)"
        )
        st.plotly_chart(fig2, use_container_width=True)

    else:
        st.warning("No door data available")

    # STORE PERFORMANCE
    st.subheader("📈 Store Performance Trend")

    perf_df = pd.DataFrame({
        "Metric": ["Footfall", "Sales", "Conversion %"],
        "Value": [footfall, sales, round(conversion,1)]
    })

    fig_line = px.line(perf_df, x="Metric", y="Value", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

    # HEATMAP
    st.subheader("🔥 Shelf Traffic Heatmap")
    fig_heat = generate_shelf_heatmap(filtered_df.values.tolist())
    st.pyplot(fig_heat)

    # INSIGHTS
    st.subheader("🧠 Insights")

    if not filtered_df.empty:

        top_zone = filtered_df["shelf"].value_counts().idxmax()
        low_sales = filtered_df.groupby("shelf")["purchase"].sum().idxmin()
        avg_dwell = filtered_df["dwell_time"].mean()

        st.success(f"🔥 High Traffic Shelf: {top_zone}")
        st.warning(f"📉 Low Sales Shelf: {low_sales}")

        st.markdown("### 💡 Suggestions")
        st.info("1️⃣ Improve product placement in high traffic shelf")
        st.info("2️⃣ Add offers/discounts to low sales shelf")

        if avg_dwell > 4:
            st.info("3️⃣ High dwell time but low purchase → pricing issue")
        else:
            st.info("3️⃣ Customers move fast → improve engagement")

    # MOVEMENT
    st.subheader("🚶 Customer Movement Intelligence")

    if not filtered_df.empty:

        filtered_df = filtered_df.sort_values(["customer_id", "id"])

        fig_scatter = px.scatter(
            filtered_df,
            x="x",
            y="y",
            color="purchase",
            size="dwell_time",
            hover_data=["customer_id", "shelf"]
        )

        fig_scatter.update_layout(
            xaxis_title="Store Width",
            yaxis_title="Store Height",
            template="plotly_white"
        )

        st.plotly_chart(fig_scatter, use_container_width=True)

        # PATH
        fig_path = go.Figure()

        for cid, group in filtered_df.groupby("customer_id"):
            group = group.sort_values("id")

            fig_path.add_trace(go.Scatter(
                x=group["x"],
                y=group["y"],
                mode="lines+markers",
                showlegend=False
            ))

        fig_path.update_layout(
            title="Customer Movement Path",
            xaxis_title="Store Width",
            yaxis_title="Store Height"
        )

        st.plotly_chart(fig_path, use_container_width=True)

    # SUSPECT TRACKING
    if not sus_df.empty:

        st.markdown("### 🔴 Suspect Movement Tracking")

        fig_alert = go.Figure()

        for cid, group in filtered_df.groupby("customer_id"):
            group = group.sort_values("id")

            color = "red" if cid in sus_df["Customer ID"].values else "gray"

            fig_alert.add_trace(go.Scatter(
                x=group["x"],
                y=group["y"],
                mode="lines+markers",
                line=dict(color=color, width=3 if color=="red" else 1),
                showlegend=False
            ))

        st.plotly_chart(fig_alert, use_container_width=True)

    # SHELF SALES
    st.subheader("📊 Shelf-wise Sales")

    shelf_perf = filtered_df.groupby("shelf")["purchase"].sum().reset_index()
    fig_area = px.area(shelf_perf, x="shelf", y="purchase")
    st.plotly_chart(fig_area, use_container_width=True)

    # ALERTS
    st.subheader("🚨 Suspicious Customers")

    if sus_df.empty:
        st.success("✅ No suspicious activity detected")
    else:
        main_sus = sus_df.iloc[0]

        st.markdown(f"""
        ### ⚠️ Suspect Identified
        - Customer ID: {main_sus['Customer ID']}
        - Brand: {main_sus['Brand']}
        - Shelf: {main_sus['Shelf']}
        """)

        st.dataframe(sus_df)
# =========================================================
# 🔵 MODE 2
# =========================================================
if mode == "Mode 2":

    st.header("🔵 Zone Intelligence Dashboard")

    zone_rows = fetch_zone_data()

    if not zone_rows:
        st.warning("Run zone analyzer first.")
        st.stop()

    df = pd.DataFrame(zone_rows, columns=[
        "customer_id","zone_row","zone_col","dwell_time","x","y"
    ])

    # KPIs
    st.subheader("📊 Store Overview")

    c1, c2, c3 = st.columns(3)

    c1.metric("👥 Footfall", df["customer_id"].nunique())
    c2.metric("📍 Visits", len(df))
    c3.metric("⏱ Avg Dwell", round(df["dwell_time"].mean(), 2))

    # =========================
    # 🧠 ZONE GRID HEATMAP
    # =========================
    st.subheader("🧠 Unified Zone Map")

    fig = go.Figure()
    GRID = 6

    # Draw grid
    for i in range(GRID + 1):
        fig.add_shape(type="line", x0=0, x1=GRID, y0=i, y1=i)
        fig.add_shape(type="line", x0=i, x1=i, y0=0, y1=GRID)

    # Density
    density = df.groupby(["zone_row","zone_col"]).size().reset_index(name="visits")

    df2 = df.merge(density, on=["zone_row","zone_col"])

    # Color logic
    def get_color(visits):
        if visits < 5:
            return "green"
        elif visits < 15:
            return "orange"
        else:
            return "red"

    # Plot
    fig.add_trace(go.Scatter(
        x=df2["zone_col"],
        y=df2["zone_row"],
        mode="markers",
        marker=dict(
            size=(df2["visits"]/df2["visits"].max())*30 + 5,
            color=df2["visits"].apply(get_color)
        ),
        text=df2["visits"],
        hovertemplate="Visits: %{text}"
    ))

    # =========================
    # 🔴 RISK ZONES
    # =========================
    for _, row in density.iterrows():

        r = row["zone_row"]
        c = row["zone_col"]
        visits = row["visits"]

        avg_d = df[
            (df["zone_row"] == r) &
            (df["zone_col"] == c)
        ]["dwell_time"].mean()

        # Crowded fast movement → theft risk
        if visits > 20 and avg_d < 2:
            fig.add_shape(
                type="rect",
                x0=c-0.5, x1=c+0.5,
                y0=r-0.5, y1=r+0.5,
                line=dict(color="red", width=3)
            )

        # Low traffic but high dwell → hidden zone
        elif visits < 5 and avg_d > 5:
            fig.add_shape(
                type="rect",
                x0=c-0.5, x1=c+0.5,
                y0=r-0.5, y1=r+0.5,
                line=dict(color="black", width=3)
            )

    fig.update_layout(
        title="Zone Heatmap",
        xaxis_title="Zone Column",
        yaxis_title="Zone Row",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # 🚶 MOVEMENT
    # =========================
    st.subheader("🚶 Movement Pattern")

    fig2 = px.scatter(
        df,
        x="x",
        y="y",
        size="dwell_time",
        hover_data=["customer_id"]
    )

    fig2.update_layout(
        xaxis_title="Store Width",
        yaxis_title="Store Height"
    )

    st.plotly_chart(fig2, use_container_width=True)

    # =========================
    # 🧠 INSIGHTS
    # =========================
    st.subheader("🧠 Insights")

    top = density.sort_values("visits", ascending=False).iloc[0]
    st.success(f"🔥 Top Zone: ({top['zone_row']},{top['zone_col']})")

    st.markdown("### 🚨 Risk Zones")

    for _, r in density.iterrows():

        visits = r["visits"]

        avg_d = df[
            (df["zone_row"] == r["zone_row"]) &
            (df["zone_col"] == r["zone_col"])
        ]["dwell_time"].mean()

        if visits > 20 and avg_d < 2:
            st.warning(f"Zone ({r['zone_row']},{r['zone_col']}) → Crowded Theft Risk")

        elif visits < 5 and avg_d > 5:
            st.warning(f"Zone ({r['zone_row']},{r['zone_col']}) → Hidden Risk")

    # =========================
    # 💡 SUGGESTIONS
    # =========================
    st.markdown("### 💡 Suggestions")

    st.info("1️⃣ Add staff in high traffic zones")
    st.info("2️⃣ Improve surveillance in risky areas")
    st.info("3️⃣ Optimize layout for better flow")
