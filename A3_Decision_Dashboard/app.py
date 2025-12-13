import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="X-Company | Decision Dashboard",
    layout="wide"
)

# --------------------------------------------------
# REQUIRED SCHEMA
# --------------------------------------------------
REQUIRED_COLUMNS = [
    "Order Date",
    "Sales",
    "Profit",
    "Discount",
    "Region",
    "Category",
    "Sub-Category",
    "State",
    "Order ID"
]

# --------------------------------------------------
# SIDEBAR — DATA INPUT
# --------------------------------------------------
st.sidebar.header("📂 Data Input")

uploaded_file = st.sidebar.file_uploader(
    "Upload sales CSV (optional)",
    type=["csv"]
)

# --------------------------------------------------
# LOAD DEFAULT DATA (repo root)
# --------------------------------------------------
@st.cache_data
def load_default_data():
    df = pd.read_csv("sales_data.csv", encoding="latin1")
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df

# --------------------------------------------------
# LOAD UPLOADED DATA (raw)
# --------------------------------------------------
def load_uploaded_data(file):
    return pd.read_csv(file, encoding="latin1")

# --------------------------------------------------
# SCHEMA VALIDATION + MAPPING
# --------------------------------------------------
def schema_mapper(raw_df):
    missing = [c for c in REQUIRED_COLUMNS if c not in raw_df.columns]

    if not missing:
        return raw_df, True

    st.error("❌ Uploaded dataset does not match the required structure.")
    st.markdown("### 🔧 Map your columns to continue")

    mapping = {}

    for req_col in missing:
        mapping[req_col] = st.selectbox(
            f"Select column for **{req_col}**",
            options=["— Select —"] + list(raw_df.columns),
            key=req_col
        )

    if st.button("✅ Apply Mapping"):
        if "— Select —" in mapping.values():
            st.warning("Please map all required columns.")
            st.stop()

        rename_dict = {v: k for k, v in mapping.items()}
        raw_df = raw_df.rename(columns=rename_dict)

    NUMERIC_COLS = ["Sales", "Profit", "Discount"]

for col in NUMERIC_COLS:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace("₹", "", regex=False)
    )
    df[col] = pd.to_numeric(df[col], errors="coerce")

if df[NUMERIC_COLS].isna().any().any():
    st.error("❌ One or more numeric columns contain invalid values after mapping.")
    st.stop()
    try:
            raw_df["Order Date"] = pd.to_datetime(raw_df["Order Date"])
    except Exception:
            st.error("Order Date could not be parsed as a date.")
            st.stop()

return raw_df, True

    st.stop()

# --------------------------------------------------
# DATA SELECTION LOGIC
# --------------------------------------------------
if uploaded_file is not None:
    raw_df = load_uploaded_data(uploaded_file)
    df, ready = schema_mapper(raw_df)
else:
    df = load_default_data()
    ready = True

if not ready:
    st.stop()

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("📊 Sales Decision Dashboard")
st.caption("Executive view focused on actions, risks, and priorities")
st.divider()

# --------------------------------------------------
# KPI SNAPSHOT
# --------------------------------------------------
total_sales = df["Sales"].sum()
total_profit = df["Profit"].sum()
loss_orders = df[(df["Discount"] >= 0.3) & (df["Profit"] < 0)]

k1, k2, k3 = st.columns(3)
k1.metric("Total Sales", f"${total_sales:,.0f}")
k2.metric("Total Profit", f"${total_profit:,.0f}")
k3.metric("High-Discount Loss Orders", f"{len(loss_orders):,}")

st.divider()

# --------------------------------------------------
# DECISION GRID (2 × 2)
# --------------------------------------------------
c1, c2 = st.columns(2)

# 1️⃣ Category Risk
with c1:
    cat_profit = (
        df.groupby("Category")["Profit"]
        .sum()
        .reset_index()
        .sort_values("Profit")
    )

    fig_cat = px.bar(
        cat_profit,
        x="Profit",
        y="Category",
        orientation="h",
        title="Profit by Category (Risk Exposure)",
        color="Profit",
        color_continuous_scale="RdBu"
    )
    st.plotly_chart(fig_cat, use_container_width=True)

# 2️⃣ Discount Risk Curve
with c2:
    df["Discount Bucket"] = pd.cut(
        df["Discount"],
        bins=[0, 0.1, 0.2, 0.3, 0.4, 1],
        labels=["0–10%", "10–20%", "20–30%", "30–40%", "40%+"]
    )

    bucket_profit = (
        df.groupby("Discount Bucket")["Profit"]
        .sum()
        .reset_index()
    )

    fig_disc = px.line(
        bucket_profit,
        x="Discount Bucket",
        y="Profit",
        markers=True,
        title="Profit Impact by Discount Level"
    )
    st.plotly_chart(fig_disc, use_container_width=True)

# --------------------------------------------------
# SECOND ROW
# --------------------------------------------------
c3, c4 = st.columns(2)

# 3️⃣ Regional Priority
with c3:
    region_profit = (
        df.groupby("Region")["Profit"]
        .sum()
        .reset_index()
        .sort_values("Profit")
    )

    fig_reg = px.bar(
        region_profit,
        x="Profit",
        y="Region",
        orientation="h",
        title="Profit by Region (Action Priority)",
        color="Profit",
        color_continuous_scale="RdBu"
    )
    st.plotly_chart(fig_reg, use_container_width=True)

# 4️⃣ Worst Sub-Categories
with c4:
    subcat_loss = (
        df.groupby("Sub-Category")["Profit"]
        .sum()
        .reset_index()
        .sort_values("Profit")
        .head(10)
    )

    fig_sub = px.bar(
        subcat_loss,
        x="Profit",
        y="Sub-Category",
        orientation="h",
        title="Top Loss-Making Sub-Categories",
        color="Profit",
        color_continuous_scale="Reds"
    )
    st.plotly_chart(fig_sub, use_container_width=True)

st.divider()

# --------------------------------------------------
# DECISION SUMMARY
# --------------------------------------------------
st.subheader("📌 Decision Summary")

st.markdown(f"""
• **{len(loss_orders):,} orders** are generating losses due to discounts ≥ 30%  
• Loss concentration is highest in **Tables, Bookcases, Supplies**  
• **Technology and Phones** remain the strongest profit drivers  
• Profit declines sharply beyond the **20–30% discount range**
""")

st.subheader("✅ Recommended Actions")

st.markdown("""
• Cap discounts at **≤20%** for low-margin categories  
• Protect high-margin categories from blanket promotions  
• Prioritize intervention in **loss-heavy regions** before expanding sales  
• Track **profit-first KPIs**, not sales-only growth
""")

# --------------------------------------------------
# EXPORTABLE NARRATIVE
# --------------------------------------------------
st.subheader("📄 Decision Narrative (for report)")

narrative = f"""
During the review period, total sales reached ${total_sales:,.0f} with overall
profit of ${total_profit:,.0f}. Analysis shows that aggressive discounting beyond
30% is a primary driver of losses, accounting for {len(loss_orders):,} unprofitable
orders.

Profit leakage is concentrated in specific product categories and regions,
indicating targeted intervention opportunities. Reducing high-risk discounting
and prioritizing high-margin products is expected to stabilize profitability
without sacrificing core revenue streams.
"""

st.text_area("Narrative", narrative, height=220)
