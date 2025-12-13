import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ===============================
# Page config
# ===============================
st.set_page_config(
    page_title="X-Company AI Sales Intelligence",
    layout="wide"
)

# ===============================
# Styling (light futuristic vibe)
# ===============================
st.markdown("""
<style>
h1, h2, h3 { letter-spacing: 0.5px; }
.metric-label { font-size: 14px; color: #999; }
</style>
""", unsafe_allow_html=True)

# ===============================
# Helpers
# ===============================
def fmt_money(x):
    if abs(x) >= 1_000_000:
        return f"${x/1_000_000:.2f}M"
    if abs(x) >= 1_000:
        return f"${x/1_000:.1f}K"
    return f"${x:,.0f}"

def load_data(uploaded=None):
    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded, encoding="latin1")
            if df.empty:
                raise ValueError
        except Exception:
            df = pd.read_csv("superstore_sales.csv", encoding="latin1")
    else:
        df = pd.read_csv("superstore_sales.csv", encoding="latin1")

    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    for c in ["Sales", "Profit", "Discount", "Quantity"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    return df.dropna(subset=["Order Date"])

# ===============================
# Sidebar
# ===============================
st.sidebar.header("📂 Data Input")
uploaded = st.sidebar.file_uploader(
    "Upload company sales CSV (optional)",
    type=["csv"]
)

df = load_data(uploaded)

st.sidebar.header("🎛 Filters")

date_min, date_max = df["Order Date"].min(), df["Order Date"].max()
date_range = st.sidebar.date_input(
    "Order Date Range",
    [date_min, date_max],
    min_value=date_min,
    max_value=date_max
)

regions = st.sidebar.multiselect(
    "Region",
    sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique())
)

df_f = df[
    (df["Order Date"] >= pd.to_datetime(date_range[0])) &
    (df["Order Date"] <= pd.to_datetime(date_range[1])) &
    (df["Region"].isin(regions))
].copy()

# ===============================
# Header
# ===============================
st.title("🤖 X-Company AI Sales Intelligence")
st.caption(
    "An AI-inspired analytics dashboard explaining **why revenue and profit change** "
    "across time, products, regions, and discount behavior."
)

# ===============================
# KPIs
# ===============================
sales = df_f["Sales"].sum()
profit = df_f["Profit"].sum()
orders = df_f["Order ID"].nunique()
aov = sales / orders if orders else 0
avg_disc = df_f["Discount"].mean()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Revenue", fmt_money(sales))
k2.metric("Profit", fmt_money(profit))
k3.metric("Orders", f"{orders:,}")
k4.metric("Avg Order Value", fmt_money(aov))
k5.metric("Avg Discount", f"{avg_disc:.1%}")

st.divider()

# ===============================
# TABS
# ===============================
tabs = st.tabs([
    "📈 Trends",
    "🧩 Product Intelligence",
    "🗺 Geo Performance",
    "💥 Discount & Risk",
    "🧠 AI Insights"
])

# ===============================
# 📈 TRENDS (2x2 GRID)
# ===============================
with tabs[0]:
    st.subheader("📈 Performance Trends")

    monthly = (
        df_f.set_index("Order Date")
        .resample("M")
        .agg({"Sales": "sum", "Profit": "sum", "Order ID": "nunique"})
        .rename(columns={"Order ID": "Orders"})
    )

    c1, c2 = st.columns(2)

    with c1:
        fig, ax = plt.subplots()
        ax.plot(monthly.index, monthly["Sales"], color="#00b4d8", linewidth=2)
        ax.set_title("Revenue Trend")
        st.pyplot(fig, clear_figure=True)

    with c2:
        fig, ax = plt.subplots()
        ax.plot(monthly.index, monthly["Profit"], color="#2ec4b6", linewidth=2)
        ax.set_title("Profit Trend")
        st.pyplot(fig, clear_figure=True)

    c3, c4 = st.columns(2)

    with c3:
        fig, ax = plt.subplots()
        ax.plot(monthly.index, monthly["Orders"], color="#ff9f1c", linewidth=2)
        ax.set_title("Orders Trend")
        st.pyplot(fig, clear_figure=True)

    with c4:
        fig, ax = plt.subplots()
        ax.plot(monthly.index, monthly["Sales"] / monthly["Orders"], color="#9b5de5")
        ax.set_title("Avg Order Value Trend")
        st.pyplot(fig, clear_figure=True)

# ===============================
# 🧩 PRODUCT INTELLIGENCE
# ===============================
with tabs[1]:
    st.subheader("🧩 Product Intelligence")

    c1, c2 = st.columns(2)

    with c1:
        cat_sales = df_f.groupby("Category")["Sales"].sum().sort_values()
        fig, ax = plt.subplots()
        cat_sales.plot(kind="barh", ax=ax, color="#4361ee")
        ax.set_title("Revenue by Category")
        st.pyplot(fig, clear_figure=True)

    with c2:
        sub_sales = (
            df_f.groupby("Sub-Category")["Sales"]
            .sum()
            .sort_values()
            .tail(10)
        )
        fig, ax = plt.subplots()
        sub_sales.plot(kind="barh", ax=ax, color="#4cc9f0")
        ax.set_title("Top Sub-Categories")
        st.pyplot(fig, clear_figure=True)

# ===============================
# 🗺 GEO PERFORMANCE
# ===============================
with tabs[2]:
    st.subheader("🗺 Regional & State Performance")

    c1, c2 = st.columns(2)

    with c1:
        reg_sales = df_f.groupby("Region")["Sales"].sum().sort_values()
        fig, ax = plt.subplots()
        reg_sales.plot(kind="barh", ax=ax, color="#f72585")
        ax.set_title("Revenue by Region")
        st.pyplot(fig, clear_figure=True)

    with c2:
        state_profit = (
            df_f.groupby("State")["Profit"]
            .sum()
            .sort_values()
            .head(10)
        )
        fig, ax = plt.subplots()
        state_profit.plot(kind="barh", ax=ax, color="#b5179e")
        ax.set_title("Worst States by Profit")
        st.pyplot(fig, clear_figure=True)

# ===============================
# 💥 DISCOUNT & RISK
# ===============================
with tabs[3]:
    st.subheader("💥 Discount Risk Analysis")

    c1, c2 = st.columns(2)

    with c1:
        fig, ax = plt.subplots()
        ax.scatter(
            df_f["Discount"],
            df_f["Profit"],
            s=df_f["Sales"] / 120,
            alpha=0.5,
            color="#ef233c"
        )
        ax.set_title("Discount vs Profit (size = revenue)")
        ax.set_xlabel("Discount")
        ax.set_ylabel("Profit")
        st.pyplot(fig, clear_figure=True)

    with c2:
        buckets = pd.cut(
            df_f["Discount"],
            bins=[0, 0.1, 0.2, 0.3, 0.4, 1],
            labels=["0–10%", "10–20%", "20–30%", "30–40%", "40%+"]
        )
        bucket_profit = df_f.groupby(buckets)["Profit"].sum()

        fig, ax = plt.subplots()
        bucket_profit.plot(marker="o", ax=ax, color="#ff006e")
        ax.set_title("Profit by Discount Bucket")
        st.pyplot(fig, clear_figure=True)

# ===============================
# 🧠 AI INSIGHTS
# ===============================
with tabs[4]:
    st.subheader("🧠 AI-Generated Business Insights")

    bullets = []
    recos = []

    if not df_f.empty:
        bullets.append(
            f"Revenue leader: **{df_f.groupby('Category')['Sales'].sum().idxmax()}**"
        )
        bullets.append(
            f"Profit drag: **{df_f.groupby('Category')['Profit'].sum().idxmin()}**"
        )

        loss_rate = ((df_f["Discount"] >= 0.3) & (df_f["Profit"] < 0)).mean() * 100
        bullets.append(
            f"High-discount loss exposure: **{loss_rate:.1f}% of orders**"
        )

        recos.extend([
            "Tighten discount controls above 30%, especially in Furniture and Supplies.",
            "Scale high-margin categories (Technology, Copiers, Accessories).",
            "Monitor profit alongside revenue — growth without margin signals risk."
        ])

    for b in bullets:
        st.markdown(f"- {b}")

    st.markdown("### Recommended Actions")
    for r in recos:
        st.markdown(f"- {r}")

    narrative = (
        "X-Company’s sales performance is driven primarily by category mix and "
        "discount strategy. While revenue growth is supported by Technology products, "
        "excessive discounting in low-margin categories introduces material profit risk. "
        "Optimizing discount thresholds and shifting mix toward high-margin products "
        "can significantly improve profitability."
    )

    st.text_area("📄 Executive-ready narrative", narrative, height=160)
