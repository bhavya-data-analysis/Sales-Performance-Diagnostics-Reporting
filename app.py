import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sales Driver Dashboard (Superstore)", layout="wide")

# ----------------------------
# Helpers
# ----------------------------
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        # Superstore files often need latin1
        df = pd.read_csv(uploaded_file, encoding="latin1")
    else:
        # Default local file name (keep in same folder)
        df = pd.read_csv("superstore_sales.csv", encoding="latin1")

    # Parse dates
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors="coerce")

    # Basic cleanup
    df = df.dropna(subset=["Order Date"])
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce").fillna(0.0)
    df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce").fillna(0.0)
    df["Discount"] = pd.to_numeric(df["Discount"], errors="coerce").fillna(0.0)
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(0)

    # Some files have blank/NaN postal codes; keep as-is
    return df


def kpi_block(df_cur, df_prev):
    def safe_pct_change(cur, prev):
        if prev is None or prev == 0:
            return None
        return (cur - prev) / prev

    sales_cur = float(df_cur["Sales"].sum())
    profit_cur = float(df_cur["Profit"].sum())
    orders_cur = df_cur["Order ID"].nunique()
    aov_cur = sales_cur / orders_cur if orders_cur else 0.0
    disc_cur = float(df_cur["Discount"].mean()) if len(df_cur) else 0.0

    sales_prev = float(df_prev["Sales"].sum()) if df_prev is not None else None
    profit_prev = float(df_prev["Profit"].sum()) if df_prev is not None else None
    orders_prev = df_prev["Order ID"].nunique() if df_prev is not None else None
    aov_prev = (sales_prev / orders_prev) if (orders_prev and sales_prev is not None) else None

    c1, c2, c3, c4, c5 = st.columns(5)

    def metric(col, label, value, prev_value, fmt=",.2f", is_money=False):
        if is_money:
            v = f"${value:{fmt}}"
        else:
            v = f"{value:{fmt}}" if isinstance(value, (int, float)) else str(value)

        delta = None
        if prev_value is not None:
            pct = safe_pct_change(value, prev_value)
            if pct is not None:
                delta = f"{pct*100:+.1f}%"
        col.metric(label, v, delta)

    metric(c1, "Total Sales", sales_cur, sales_prev, fmt=",.2f", is_money=True)
    metric(c2, "Total Profit", profit_cur, profit_prev, fmt=",.2f", is_money=True)
    metric(c3, "Orders", orders_cur, orders_prev, fmt=",.0f")
    metric(c4, "Avg Order Value", aov_cur, aov_prev, fmt=",.2f", is_money=True)
    c5.metric("Avg Discount", f"{disc_cur*100:.1f}%", None)


def period_split(df, start, end):
    """Return (current_period_df, previous_period_df) with same duration."""
    df = df.copy()
    cur = df[(df["Order Date"] >= start) & (df["Order Date"] <= end)]
    days = (end - start).days + 1
    prev_end = start - pd.Timedelta(days=1)
    prev_start = prev_end - pd.Timedelta(days=days - 1)
    prev = df[(df["Order Date"] >= prev_start) & (df["Order Date"] <= prev_end)]
    return cur, prev, prev_start, prev_end


def line_chart(df, date_col, value_col, freq="M", label="Sales"):
    g = (
        df.set_index(date_col)[value_col]
        .resample(freq)
        .sum()
        .reset_index()
        .dropna()
    )

    fig, ax = plt.subplots()
    ax.plot(g[date_col], g[value_col])
    ax.set_xlabel("Date")
    ax.set_ylabel(label)
    ax.set_title(f"{label} Trend ({freq})")
    st.pyplot(fig, clear_figure=True)
    return g


def barh_top(df, group_col, value_col, top_n=10, title="Top"):
    g = df.groupby(group_col, dropna=False)[value_col].sum().sort_values(ascending=False)
    g = g.head(top_n)
    fig, ax = plt.subplots()
    ax.barh(g.index.astype(str)[::-1], g.values[::-1])
    ax.set_title(title)
    ax.set_xlabel(value_col)
    st.pyplot(fig, clear_figure=True)
    return g


def scatter_discount_profit(df, sample_n=4000):
    d = df[["Discount", "Profit", "Sales"]].copy()
    if len(d) > sample_n:
        d = d.sample(sample_n, random_state=42)

    fig, ax = plt.subplots()
    ax.scatter(d["Discount"], d["Profit"], s=np.clip(d["Sales"].values, 5, 200))
    ax.axhline(0, linewidth=1)
    ax.set_title("Discount vs Profit (size ~ Sales)")
    ax.set_xlabel("Discount")
    ax.set_ylabel("Profit")
    st.pyplot(fig, clear_figure=True)


def insights_and_recos(df_cur, df_prev):
    # Sales/profit change drivers
    sales_cur = df_cur["Sales"].sum()
    sales_prev = df_prev["Sales"].sum() if df_prev is not None else 0
    profit_cur = df_cur["Profit"].sum()
    profit_prev = df_prev["Profit"].sum() if df_prev is not None else 0

    def pct(cur, prev):
        if prev == 0:
            return None
        return (cur - prev) / prev

    sales_pct = pct(sales_cur, sales_prev)
    profit_pct = pct(profit_cur, profit_prev)

    # Category deltas
    cat_cur = df_cur.groupby("Category")["Sales"].sum()
    cat_prev = df_prev.groupby("Category")["Sales"].sum() if df_prev is not None else pd.Series(dtype=float)
    cat_delta = (cat_cur - cat_prev.reindex(cat_cur.index).fillna(0)).sort_values()

    # Profit leaks (high discount + negative profit)
    leak = df_cur[(df_cur["Discount"] >= 0.3) & (df_cur["Profit"] < 0)]
    leak_sales = leak["Sales"].sum()
    leak_cnt = len(leak)

    # Worst sub-categories by profit
    sub_profit = df_cur.groupby("Sub-Category")["Profit"].sum().sort_values()
    worst_sub = sub_profit.head(3)
    best_sub = sub_profit.tail(3)

    bullets = []

    if sales_pct is not None:
        direction = "increased" if sales_pct >= 0 else "decreased"
        bullets.append(f"Sales **{direction} {abs(sales_pct)*100:.1f}%** vs the previous period.")
    else:
        bullets.append("Sales change vs previous period can’t be computed (previous period total was 0).")

    if profit_pct is not None:
        direction = "increased" if profit_pct >= 0 else "decreased"
        bullets.append(f"Profit **{direction} {abs(profit_pct)*100:.1f}%** vs the previous period.")
    else:
        bullets.append("Profit change vs previous period can’t be computed (previous period total was 0).")

    if len(cat_delta):
        biggest_down = cat_delta.head(1)
        biggest_up = cat_delta.tail(1)
        bullets.append(f"Biggest sales drag: **{biggest_down.index[0]}** ({biggest_down.iloc[0]:+.0f}).")
        bullets.append(f"Biggest sales lift: **{biggest_up.index[0]}** ({biggest_up.iloc[0]:+.0f}).")

    if leak_cnt > 0 and sales_cur > 0:
        bullets.append(
            f"Profit leak: **{leak_cnt:,}** orders with **Discount ≥ 30%** and **negative profit** "
            f"(~**{leak_sales/sales_cur*100:.1f}%** of sales in this period)."
        )
    else:
        bullets.append("No major discount-driven profit leak detected at the ≥30% discount threshold (for this filtered period).")

    recos = [
        f"Reduce discounting on low-margin areas — start with **{worst_sub.index[0]}**, **{worst_sub.index[1]}**, **{worst_sub.index[2]}** (worst total profit).",
        f"Double down on what’s working — strongest profit sub-categories: **{best_sub.index[-1]}**, **{best_sub.index[-2]}**, **{best_sub.index[-3]}**.",
        "Track performance weekly: watch Sales, Profit, and Discount together (a sales increase with profit drop usually signals discounting or product mix issues).",
    ]

    return bullets, recos


# ----------------------------
# UI
# ----------------------------
st.title("📈 Sales Driver Dashboard — Superstore (Rich View)")
st.caption("Answering: *Why are my sales changing?* (trends • product mix • regions • discounts • profit leaks)")

with st.sidebar:
    st.header("Data")
    up = st.file_uploader("Upload Superstore CSV (optional)", type=["csv"])
    df = load_data(up)

    st.divider()
    st.header("Filters")

    min_d = df["Order Date"].min().date()
    max_d = df["Order Date"].max().date()
    date_range = st.date_input("Order Date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)

    # Multi-select filters
    def ms(label, col):
        opts = sorted([x for x in df[col].dropna().unique().tolist()])
        return st.multiselect(label, opts, default=opts)

    regions = ms("Region", "Region")
    cats = ms("Category", "Category")
    segs = ms("Segment", "Segment")
    ship_modes = ms("Ship Mode", "Ship Mode")

    gran = st.selectbox("Trend granularity", ["Daily", "Weekly", "Monthly"], index=2)
    freq = {"Daily": "D", "Weekly": "W", "Monthly": "M"}[gran]

# Apply filters
start = pd.to_datetime(date_range[0])
end = pd.to_datetime(date_range[1])

df_f = df.copy()
df_f = df_f[(df_f["Order Date"] >= start) & (df_f["Order Date"] <= end)]
df_f = df_f[df_f["Region"].isin(regions)]
df_f = df_f[df_f["Category"].isin(cats)]
df_f = df_f[df_f["Segment"].isin(segs)]
df_f = df_f[df_f["Ship Mode"].isin(ship_modes)]

cur_df, prev_df, prev_start, prev_end = period_split(df, start, end)
# Apply same non-date filters to prev period for fair comparison
prev_df = prev_df[prev_df["Region"].isin(regions)]
prev_df = prev_df[prev_df["Category"].isin(cats)]
prev_df = prev_df[prev_df["Segment"].isin(segs)]
prev_df = prev_df[prev_df["Ship Mode"].isin(ship_modes)]

# KPIs
st.subheader("📌 Key Metrics")
kpi_block(df_f, prev_df)

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Trends",
    "Product Mix",
    "Regions",
    "Discount & Profit",
    "Insights & Recommendations",
])

with tab1:
    st.subheader("📈 Trends")
    left, right = st.columns(2)

    with left:
        st.markdown("**Sales Trend**")
        _ = line_chart(df_f, "Order Date", "Sales", freq=freq, label="Sales")

    with right:
        st.markdown("**Profit Trend**")
        _ = line_chart(df_f, "Order Date", "Profit", freq=freq, label="Profit")

    st.markdown("**Orders Trend (count of unique Order ID)**")
    orders_ts = (
        df_f.set_index("Order Date")["Order ID"]
        .resample(freq)
        .nunique()
        .reset_index()
        .dropna()
    )
    fig, ax = plt.subplots()
    ax.plot(orders_ts["Order Date"], orders_ts["Order ID"])
    ax.set_title(f"Orders Trend ({freq})")
    ax.set_xlabel("Date")
    ax.set_ylabel("Orders")
    st.pyplot(fig, clear_figure=True)

with tab2:
    st.subheader("🧩 Product Mix")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Sales by Category**")
        _ = barh_top(df_f, "Category", "Sales", top_n=10, title="Category Sales (Top)")

        st.markdown("**Profit by Category**")
        _ = barh_top(df_f, "Category", "Profit", top_n=10, title="Category Profit (Top)")

    with c2:
        st.markdown("**Top Sub-Categories by Sales**")
        _ = barh_top(df_f, "Sub-Category", "Sales", top_n=12, title="Sub-Category Sales (Top 12)")

        st.markdown("**Worst Sub-Categories by Profit**")
        worst = df_f.groupby("Sub-Category")["Profit"].sum().sort_values().head(12)
        fig, ax = plt.subplots()
        ax.barh(worst.index.astype(str)[::-1], worst.values[::-1])
        ax.set_title("Sub-Category Profit (Worst 12)")
        ax.set_xlabel("Profit")
        st.pyplot(fig, clear_figure=True)

    st.markdown("**Top Products by Sales**")
    _ = barh_top(df_f, "Product Name", "Sales", top_n=10, title="Top 10 Products by Sales")

with tab3:
    st.subheader("🗺️ Regions")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Sales by Region**")
        _ = barh_top(df_f, "Region", "Sales", top_n=10, title="Region Sales")

        st.markdown("**Profit by Region**")
        _ = barh_top(df_f, "Region", "Profit", top_n=10, title="Region Profit")

    with c2:
        st.markdown("**Top States by Sales**")
        _ = barh_top(df_f, "State", "Sales", top_n=12, title="Top 12 States by Sales")

        st.markdown("**Worst States by Profit**")
        worst_states = df_f.groupby("State")["Profit"].sum().sort_values().head(12)
        fig, ax = plt.subplots()
        ax.barh(worst_states.index.astype(str)[::-1], worst_states.values[::-1])
        ax.set_title("Worst 12 States by Profit")
        ax.set_xlabel("Profit")
        st.pyplot(fig, clear_figure=True)

with tab4:
    st.subheader("💥 Discount & Profit")
    st.markdown("This section helps explain *sales changes with profit drops* (often caused by discounting or mix shifts).")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Discount vs Profit**")
        scatter_discount_profit(df_f)

    with c2:
        st.markdown("**Profitability by Discount Bucket**")
        bins = [-0.001, 0.0, 0.1, 0.2, 0.3, 0.4, 1.0]
        labels = ["0%", "0–10%", "10–20%", "20–30%", "30–40%", "40%+"]
        d = df_f.copy()
        d["Discount Bucket"] = pd.cut(d["Discount"], bins=bins, labels=labels)
        bucket = d.groupby("Discount Bucket")[["Sales", "Profit"]].sum()

        fig, ax = plt.subplots()
        ax.plot(bucket.index.astype(str), bucket["Profit"].values, marker="o")
        ax.set_title("Total Profit by Discount Bucket")
        ax.set_xlabel("Discount Bucket")
        ax.set_ylabel("Profit")
        st.pyplot(fig, clear_figure=True)

    st.markdown("**High Discount + Negative Profit Orders (Potential Leak List)**")
    leak_df = df_f[(df_f["Discount"] >= 0.3) & (df_f["Profit"] < 0)].copy()
    show_cols = ["Order Date", "Order ID", "Category", "Sub-Category", "Product Name", "Sales", "Discount", "Profit", "Region", "State"]
    st.dataframe(leak_df[show_cols].sort_values("Profit").head(50), use_container_width=True)

with tab5:
    st.subheader("🧠 Insights & Recommendations")
    bullets, recos = insights_and_recos(df_f, prev_df)

    st.markdown("### What changed (summary)")
    for b in bullets:
        st.markdown(f"- {b}")

    st.markdown("### Recommended actions")
    for r in recos:
        st.markdown(f"- {r}")

    st.divider()
    st.markdown("### Export-ready narrative (copy into report)")
    sales_total = df_f["Sales"].sum()
    profit_total = df_f["Profit"].sum()
    orders_total = df_f["Order ID"].nunique()
    avg_disc = df_f["Discount"].mean()

    narrative = (
        f"In the selected period, the business generated **${sales_total:,.0f}** in sales across **{orders_total:,}** orders, "
        f"with total profit of **${profit_total:,.0f}** and an average discount of **{avg_disc*100:.1f}%**. "
        f"The trend and breakdown views indicate that changes in sales are primarily explained by product mix (category/sub-category performance), "
        f"regional performance differences, and discounting patterns that impact profitability. "
        f"Recommended next steps include tightening discounting where it produces negative margin, prioritizing high-profit sub-categories, "
        f"and monitoring weekly movement in sales and profit together to identify early warning signals."
    )
    st.text_area("Narrative", narrative, height=180)

st.caption(f"Comparison previous period: {prev_start.date()} to {prev_end.date()} (same length as your selected range).")
