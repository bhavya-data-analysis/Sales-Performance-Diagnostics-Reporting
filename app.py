import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="X-Company AI Sales Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("Sales Performance & Profit Risk Dashboard")
st.caption("Interactive analysis of sales trends, discounts, and profitability")

# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------
@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, encoding="latin1")
    else:
        df = pd.read_csv("superstore_sales.csv", encoding="latin1")

    df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.header("📂 Data Input")

uploaded_file = st.sidebar.file_uploader(
    "Upload company sales CSV (optional)",
    type=["csv"]
)

df = load_data(uploaded_file)

st.sidebar.header("🎛 Filters")

date_range = st.sidebar.date_input(
    "Order Date Range",
    [df["Order Date"].min(), df["Order Date"].max()]
)

regions = st.sidebar.multiselect(
    "Region",
    df["Region"].unique(),
    default=df["Region"].unique()
)

# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------
df_f = df[
    (df["Order Date"] >= pd.to_datetime(date_range[0])) &
    (df["Order Date"] <= pd.to_datetime(date_range[1])) &
    (df["Region"].isin(regions))
]

# --------------------------------------------------
# KPI METRICS
# --------------------------------------------------
total_sales = df_f["Sales"].sum()
total_profit = df_f["Profit"].sum()
orders = df_f["Order ID"].nunique()
avg_discount = df_f["Discount"].mean() * 100

k1, k2, k3, k4 = st.columns(4)

k1.metric("💰 Total Sales", f"${total_sales:,.0f}")
k2.metric("📈 Total Profit", f"${total_profit:,.0f}")
k3.metric("🧾 Orders", f"{orders:,}")
k4.metric("🏷 Avg Discount", f"{avg_discount:.1f}%")

st.divider()

# --------------------------------------------------
# TABS
# --------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📉 Trends",
    "🧠 Product Intelligence",
    "🌍 Geo Performance",
    "⚠️ Discount Risk",
    "🤖 AI Insights"
])

# --------------------------------------------------
# TAB 1 — TRENDS
# --------------------------------------------------
with tab1:
    st.subheader("📉 Sales & Profit Trends")

    trend = (
        df_f
        .groupby(pd.Grouper(key="Order Date", freq="M"))
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .reset_index()
    )

    c1, c2 = st.columns(2)

    with c1:
        fig_sales = px.line(
            trend,
            x="Order Date",
            y="Sales",
            title="Monthly Sales Trend",
            markers=True
        )
        st.plotly_chart(fig_sales, use_container_width=True)

    with c2:
        fig_profit = px.line(
            trend,
            x="Order Date",
            y="Profit",
            title="Monthly Profit Trend",
            markers=True
        )
        st.plotly_chart(fig_profit, use_container_width=True)

# --------------------------------------------------
# TAB 2 — PRODUCT INTELLIGENCE
# --------------------------------------------------
with tab2:
    st.subheader("🧠 Product Mix Performance")

    c1, c2 = st.columns(2)

    with c1:
        cat_sales = (
            df_f.groupby("Category")["Sales"]
            .sum()
            .reset_index()
            .sort_values("Sales", ascending=False)
        )
        fig_cat = px.bar(
            cat_sales,
            x="Sales",
            y="Category",
            orientation="h",
            title="Sales by Category",
            color="Sales",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    with c2:
        subcat_profit = (
            df_f.groupby("Sub-Category")["Profit"]
            .sum()
            .reset_index()
            .sort_values("Profit")
            .head(10)
        )
        fig_sub = px.bar(
            subcat_profit,
            x="Profit",
            y="Sub-Category",
            orientation="h",
            title="Worst Sub-Categories by Profit",
            color="Profit",
            color_continuous_scale="Reds"
        )
        st.plotly_chart(fig_sub, use_container_width=True)

# --------------------------------------------------
# TAB 3 — GEO PERFORMANCE
# --------------------------------------------------
with tab3:
    st.subheader("🌍 Regional Performance")

    c1, c2 = st.columns(2)

    with c1:
        reg_sales = df_f.groupby("Region")["Sales"].sum().reset_index()
        fig_reg = px.bar(
            reg_sales,
            x="Region",
            y="Sales",
            title="Sales by Region",
            color="Sales",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig_reg, use_container_width=True)

    with c2:
        state_sales = (
            df_f.groupby("State")["Sales"]
            .sum()
            .reset_index()
            .sort_values("Sales", ascending=False)
            .head(10)
        )
        fig_state = px.bar(
            state_sales,
            x="Sales",
            y="State",
            orientation="h",
            title="Top 10 States by Sales"
        )
        st.plotly_chart(fig_state, use_container_width=True)

# --------------------------------------------------
# TAB 4 — DISCOUNT RISK
# --------------------------------------------------
with tab4:
    st.subheader("⚠️ Discount vs Profit Risk")

    c1, c2 = st.columns(2)

    with c1:
        fig_scatter = px.scatter(
            df_f,
            x="Discount",
            y="Profit",
            size="Sales",
            title="Discount vs Profit (Bubble = Sales)",
            opacity=0.6
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with c2:
        df_f["Discount Bucket"] = pd.cut(
            df_f["Discount"],
            bins=[0, 0.1, 0.2, 0.3, 0.4, 1],
            labels=["0–10%", "10–20%", "20–30%", "30–40%", "40%+"]
        )

        bucket_profit = (
            df_f.groupby("Discount Bucket")["Profit"]
            .sum()
            .reset_index()
        )

        fig_bucket = px.line(
            bucket_profit,
            x="Discount Bucket",
            y="Profit",
            markers=True,
            title="Profit by Discount Bucket"
        )
        st.plotly_chart(fig_bucket, use_container_width=True)

# --------------------------------------------------
# TAB 5 — AI INSIGHTS
# --------------------------------------------------
with tab5:
    st.subheader("🤖 AI-Style Insights & Recommendations")

    loss_orders = df_f[(df_f["Discount"] >= 0.3) & (df_f["Profit"] < 0)]

    st.markdown("### 🔍 Key Findings")
    st.markdown(f"""
    • **{len(loss_orders):,} orders** have high discounts (≥30%) with **negative profit**  
    • Biggest profit leakage occurs in **Tables, Bookcases, Supplies**  
    • **Technology & Phones** drive the strongest profit growth  
    """)

    st.markdown("### ✅ Recommended Actions")
    st.markdown("""
    • Reduce aggressive discounting in low-margin categories  
    • Protect high-margin products from unnecessary promotions  
    • Monitor **Sales + Profit + Discount together** weekly  
    """)

    st.markdown("### 📄 Export-Ready Narrative")
    narrative = f"""
X-Company experienced total sales of ${total_sales:,.0f} with profit of ${total_profit:,.0f}
during the selected period. While sales grew across regions, profitability declined in
areas with aggressive discounting. Orders with discounts above 30% accounted for a
disproportionate share of losses. Strategic discount control and focus on high-margin
products is recommended.
    """
    st.text_area("Narrative", narrative, height=200)
