import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -----------------------
# Page config
# -----------------------
st.set_page_config(
    page_title="Sales Driver Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------
# Helpers
# -----------------------
def fmt_money(x):
    if abs(x) >= 1_000_000:
        return f"${x/1_000_000:.2f}M"
    if abs(x) >= 1_000:
        return f"${x/1_000:.1f}K"
    return f"${x:,.0f}"

def load_data(uploaded_file=None):
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, encoding="latin1")
            if df.empty:
                raise ValueError
        except Exception:
            df = pd.read_csv("superstore_sales.csv", encoding="latin1")
    else:
        df = pd.read_csv("superstore_sales.csv", encoding="latin1")

    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors="coerce")

    for col in ["Sales", "Profit", "Discount", "Quantity"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df = df.dropna(subset=["Order Date"])
    return df

# -----------------------
# Sidebar
# -----------------------
st.sidebar.header("📂 Data")
uploaded = st.sidebar.file_uploader(
    "Upload your sales CSV (optional)",
    type=["csv"]
)

df = load_data(uploaded)

st.sidebar.header("🎛 Filters")

min_d, max_d = df["Order Date"].min(), df["Order Date"].max()
date_range = st.sidebar.date_input(
    "Order Date range",
    [min_d, max_d],
    min_value=min_d,
    max_value=max_d
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

# -----------------------
# Header
# -----------------------
st.title("📈 Sales Driver Dashboard — Superstore")
st.caption(
    "Answering **why sales change** using trends, product mix, regions, "
    "discount behavior, and profit leaks."
)

# -----------------------
# KPIs
# -----------------------
total_sales = df_f["Sales"].sum()
total_profit = df_f["Profit"].sum()
orders = df_f["Order ID"].nunique()
aov = total_sales / orders if orders else 0
avg_discount = df_f["Discount"].mean()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Sales", fmt_money(total_sales))
c2.metric("Total Profit", fmt_money(total_profit))
c3.metric("Orders", f"{orders:,}")
c4.metric("Avg Order Value", fmt_money(aov))
c5.metric("Avg Discount", f"{avg_discount:.1%}")

st.divider()

# -----------------------
# Tabs
# -----------------------
tabs = st.tabs([
    "📉 Trends",
    "🧩 Product Mix",
    "🗺 Regions",
    "💥 Discount & Profit",
    "🧠 Insights & Recommendations"
])

# -----------------------
# Trends
# -----------------------
with tabs[0]:
    st.subheader("📉 Trends")

    monthly = (
        df_f
        .set_index("Order Date")
        .resample("M")
        .agg({"Sales": "sum", "Profit": "sum", "Order ID": "nunique"})
        .rename(columns={"Order ID": "Orders"})
    )

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(monthly.index, monthly["Sales"], color="#1f77b4", linewidth=2)
    ax.set_title("Sales Trend")
    st.pyplot(fig, clear_figure=True)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(monthly.index, monthly["Profit"], color="#2ca02c", linewidth=2)
    ax.set_title("Profit Trend")
    st.pyplot(fig, clear_figure=True)

# -----------------------
# Product Mix
# -----------------------
with tabs[1]:
    st.subheader("🧩 Product Mix")

    cat_sales = df_f.groupby("Category")["Sales"].sum().sort_values()
    fig, ax = plt.subplots(figsize=(6, 4))
    cat_sales.plot(kind="barh", ax=ax, color="#9467bd")
    ax.set_title("Sales by Category")
    st.pyplot(fig, clear_figure=True)

# -----------------------
# Regions
# -----------------------
with tabs[2]:
    st.subheader("🗺 Regions")

    region_sales = df_f.groupby("Region")["Sales"].sum().sort_values()
    fig, ax = plt.subplots(figsize=(6, 4))
    region_sales.plot(kind="barh", ax=ax, color="#ff7f0e")
    ax.set_title("Sales by Region")
    st.pyplot(fig, clear_figure=True)

# -----------------------
# Discount & Profit
# -----------------------
with tabs[3]:
    st.subheader("💥 Discount & Profit")

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(
        df_f["Discount"],
        df_f["Profit"],
        s=df_f["Sales"] / 100,
        alpha=0.5,
        color="#d62728"
    )
    ax.set_xlabel("Discount")
    ax.set_ylabel("Profit")
    ax.set_title("Discount vs Profit (size = Sales)")
    st.pyplot(fig, clear_figure=True)

    st.markdown("**High Discount + Negative Profit Orders (Potential Leak List)**")

    leak_df = df_f[(df_f["Discount"] >= 0.3) & (df_f["Profit"] < 0)].copy()
    show_cols = [
        "Order Date", "Order ID", "Category", "Sub-Category",
        "Product Name", "Sales", "Discount", "Profit"
    ]

    if not leak_df.empty:
        st.dataframe(
            leak_df[show_cols].sort_values("Profit").head(50),
            use_container_width=True
        )
    else:
        st.info("No high-discount, negative-profit orders found for the selected filters.")

# -----------------------
# Insights & Recommendations
# -----------------------
with tabs[4]:
    st.subheader("🧠 Insights & Recommendations")

    bullets = []
    recos = []

    if not df_f.empty:
        top_cat = df_f.groupby("Category")["Sales"].sum().idxmax()
        worst_cat = df_f.groupby("Category")["Profit"].sum().idxmin()

        bullets.append(f"Biggest sales driver: **{top_cat}**.")
        bullets.append(f"Largest profit drag: **{worst_cat}**.")

        high_disc_loss = (df_f["Discount"] >= 0.3) & (df_f["Profit"] < 0)
        pct_loss = high_disc_loss.mean() * 100

        bullets.append(
            f"High discounts (≥30%) account for **{pct_loss:.1f}%** of orders with losses."
        )

        recos.extend([
            "Reduce discounting in low-margin categories (Tables, Bookcases, Supplies).",
            "Double down on profitable sub-categories (Copiers, Phones, Accessories).",
            "Track Sales and Profit together — sales growth with falling profit signals discount leakage."
        ])

    st.markdown("### What changed (summary)")
    for b in bullets:
        st.markdown(f"- {b}")

    st.markdown("### Recommended actions")
    for r in recos:
        st.markdown(f"- {r}")

    narrative = (
        "Sales performance is primarily driven by category mix and discount behavior. "
        "While Technology leads revenue growth, aggressive discounting in low-margin "
        "categories creates profit leakage. Tightening discount controls and shifting "
        "focus toward high-margin products can materially improve profitability."
        if bullets else ""
    )

    if isinstance(narrative, str) and narrative.strip():
        st.text_area("Export-ready narrative", narrative, height=160)
    else:
        st.info("Narrative summary not available for the selected filters.")
