"""
Supermarket Sales Analysis — Streamlit Dashboard
Dataset: supermarket_sales_500_rows.csv
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path

# ──────────────────────────────────────────────
# Page configuration
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Supermarket Sales Analysis",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Global style tweaks
# ──────────────────────────────────────────────
st.markdown(
    """
    <style>
        .metric-box {
            background: #f7f8fa;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 16px 20px;
            text-align: center;
        }
        .metric-label { font-size: 13px; color: #57606a; margin-bottom: 4px; }
        .metric-value { font-size: 28px; font-weight: 700; color: #1f2328; }
        .metric-sub   { font-size: 12px; color: #57606a; margin-top: 2px; }
        .section-title { font-size: 20px; font-weight: 600; color: #1f2328;
                         border-bottom: 2px solid #3b82d4; padding-bottom: 6px;
                         margin-top: 8px; margin-bottom: 16px; }
        .insight-card {
            background: #eef4ff;
            border-left: 4px solid #3b82d4;
            border-radius: 4px;
            padding: 12px 16px;
            margin-bottom: 10px;
            font-size: 14px;
            color: #1f2328;
        }
        .warn-card {
            background: #fff8e1;
            border-left: 4px solid #f59e0b;
            border-radius: 4px;
            padding: 12px 16px;
            margin-bottom: 10px;
            font-size: 14px;
            color: #1f2328;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
PALETTE = ["#3b82d4", "#7c5cd8", "#22c55e", "#f59e0b", "#ef4444",
           "#06b6d4", "#ec4899", "#84cc16", "#f97316"]

def fmt_inr(value: float) -> str:
    """Format a number as Indian Rupees (₹) with commas."""
    return f"₹{value:,.2f}"


def metric_card(label: str, value: str, sub: str = "") -> str:
    return (
        f'<div class="metric-box">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'<div class="metric-sub">{sub}</div>'
        f"</div>"
    )


def section(title: str):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def insight(text: str):
    st.markdown(f'<div class="insight-card">💡 {text}</div>', unsafe_allow_html=True)


def warn(text: str):
    st.markdown(f'<div class="warn-card">⚠️ {text}</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Step 1 — Load data
# ──────────────────────────────────────────────
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["Date"])
    return df


CSV_PATH = "supermarket_sales_500_rows.csv"

if not Path(CSV_PATH).exists():
    st.error(f"Dataset not found: **{CSV_PATH}**  \nPlace it in the same folder as this script.")
    st.stop()

raw_df = load_data(CSV_PATH)

# ──────────────────────────────────────────────
# Step 2 — Data quality check
# ──────────────────────────────────────────────
@st.cache_data
def quality_report(df: pd.DataFrame) -> dict:
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    duplicates = df.duplicated().sum()
    neg_qty = (df["Quantity"] < 0).sum() if "Quantity" in df.columns else 0
    neg_price = (df["Unit Price"] < 0).sum() if "Unit Price" in df.columns else 0
    neg_sales = (df["Sales"] < 0).sum() if "Sales" in df.columns else 0
    rating_range = df["Rating"].between(0, 5).all() if "Rating" in df.columns else True
    return {
        "missing": missing,
        "missing_pct": missing_pct,
        "duplicates": duplicates,
        "neg_qty": neg_qty,
        "neg_price": neg_price,
        "neg_sales": neg_sales,
        "rating_ok": rating_range,
        "shape": df.shape,
    }


# ──────────────────────────────────────────────
# Step 3 — Recalculate Sales & clean
# ──────────────────────────────────────────────
@st.cache_data
def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Recalculate Sales = Quantity × Unit Price (rounded to 2 dp)
    df["Sales_Calc"] = (df["Quantity"] * df["Unit Price"]).round(2)
    # Flag mismatches (tolerance ±0.02 for float rounding)
    df["Sales_Mismatch"] = ~np.isclose(df["Sales"], df["Sales_Calc"], atol=0.02)
    # Use the freshly calculated column going forward
    df["Sales"] = df["Sales_Calc"]
    # Derived time columns
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    df["Month_dt"] = df["Date"].dt.to_period("M").dt.to_timestamp()
    df["DayOfWeek"] = df["Date"].dt.day_name()
    return df


qr = quality_report(raw_df)
df = prepare_data(raw_df)

# ──────────────────────────────────────────────
# Sidebar — Global Filters
# ──────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg",
        width=80,
    )
    st.title("🛒 Supermarket Sales")
    st.markdown("---")
    st.subheader("🔍 Filters")

    all_cities = sorted(df["City"].unique().tolist())
    sel_cities = st.multiselect("City", all_cities, default=all_cities)

    all_categories = sorted(df["Category"].unique().tolist())
    sel_categories = st.multiselect("Category", all_categories, default=all_categories)

    all_customer = sorted(df["Customer Type"].unique().tolist())
    sel_customer = st.multiselect("Customer Type", all_customer, default=all_customer)

    all_payment = sorted(df["Payment"].unique().tolist())
    sel_payment = st.multiselect("Payment Method", all_payment, default=all_payment)

    date_min = df["Date"].min().date()
    date_max = df["Date"].max().date()
    date_range = st.date_input("Date Range", value=(date_min, date_max),
                               min_value=date_min, max_value=date_max)

    st.markdown("---")
    st.caption("IBM SkillsBuild · Data Analytics 2026")

# Apply filters
if len(date_range) == 2:
    start_d, end_d = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start_d, end_d = df["Date"].min(), df["Date"].max()

fdf = df[
    df["City"].isin(sel_cities) &
    df["Category"].isin(sel_categories) &
    df["Customer Type"].isin(sel_customer) &
    df["Payment"].isin(sel_payment) &
    df["Date"].between(start_d, end_d)
].copy()

# ──────────────────────────────────────────────
# Page Header
# ──────────────────────────────────────────────
st.title("🛒 Supermarket Sales Analysis Dashboard")
st.markdown(
    f"Analysing **{len(fdf):,}** transactions "
    f"from **{start_d.date()}** to **{end_d.date()}**  |  "
    f"Cities: {', '.join(sel_cities)}  |  Categories: {', '.join(sel_categories)}"
)

# ──────────────────────────────────────────────
# Tabs
# ──────────────────────────────────────────────
tabs = st.tabs([
    "📋 Data Overview",
    "🔬 Data Quality",
    "📊 Sales Summary",
    "📈 Trend Analysis",
    "🗂️ Category & Product",
    "🏙️ City & Branch",
    "👥 Customer Insights",
    "💳 Payment Analysis",
    "💡 Business Decisions",
])

# ═══════════════════════════════════════════════════════════
# TAB 0 — DATA OVERVIEW
# ═══════════════════════════════════════════════════════════
with tabs[0]:
    section("📋 Dataset Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(metric_card("Total Records", f"{qr['shape'][0]:,}", "rows in dataset"), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card("Columns", f"{qr['shape'][1]}", "features"), unsafe_allow_html=True)
    with col3:
        st.markdown(metric_card("Date Range", f"{raw_df['Date'].min().date()}", f"to {raw_df['Date'].max().date()}"), unsafe_allow_html=True)
    with col4:
        st.markdown(metric_card("Cities", f"{raw_df['City'].nunique()}", ", ".join(sorted(raw_df['City'].unique()))), unsafe_allow_html=True)

    st.markdown("#### Column Reference")
    col_desc = {
        "Invoice ID": "Unique transaction identifier",
        "Date": "Transaction date",
        "Branch": "Store branch code (A / B / C / D)",
        "City": "City of the branch",
        "Customer Type": "Member or Normal customer",
        "Gender": "Customer gender",
        "Product": "Product name",
        "Category": "Product category",
        "Quantity": "Units purchased",
        "Unit Price": "Price per unit (₹)",
        "Payment": "Payment method used",
        "Rating": "Customer satisfaction (0–5)",
        "Sales": "Quantity × Unit Price (₹)",
    }
    st.dataframe(
        pd.DataFrame(list(col_desc.items()), columns=["Column", "Description"]),
        hide_index=True, use_container_width=True,
    )

    st.markdown("#### Sample Data (first 10 rows)")
    st.dataframe(
        raw_df.head(10).style.format({"Unit Price": "₹{:.2f}", "Sales": "₹{:.2f}"}),
        use_container_width=True,
    )

    st.markdown("#### Statistical Summary")
    st.dataframe(
        df[["Quantity", "Unit Price", "Sales", "Rating"]]
        .describe()
        .round(2)
        .style.format("{:.2f}"),
        use_container_width=True,
    )

# ═══════════════════════════════════════════════════════════
# TAB 1 — DATA QUALITY
# ═══════════════════════════════════════════════════════════
with tabs[1]:
    section("🔬 Data Quality Report")

    total_missing = int(qr["missing"].sum())
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card("Missing Values", str(total_missing), "across all columns"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("Duplicate Rows", str(qr["duplicates"]), "exact row duplicates"), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("Negative Quantities", str(qr["neg_qty"]), "invalid records"), unsafe_allow_html=True)
    with c4:
        st.markdown(metric_card("Negative Prices", str(qr["neg_price"]), "invalid records"), unsafe_allow_html=True)

    # Missing values table
    miss_df = pd.DataFrame({
        "Column": qr["missing"].index,
        "Missing Count": qr["missing"].values,
        "Missing %": qr["missing_pct"].values,
    })
    st.markdown("#### Missing Values per Column")
    st.dataframe(miss_df.style.format({"Missing %": "{:.2f}%"}), hide_index=True, use_container_width=True)

    # Sales recalculation check
    mismatch_count = int(df["Sales_Mismatch"].sum())
    st.markdown("#### Sales Recalculation Verification (Qty × Unit Price)")
    if mismatch_count == 0:
        st.success(f"✅ All {len(df):,} Sales values match Quantity × Unit Price exactly (tolerance ±₹0.02).")
    else:
        st.warning(f"⚠️ {mismatch_count} rows had Sales ≠ Quantity × Unit Price. Recalculated values are used throughout this dashboard.")
        st.dataframe(
            df[df["Sales_Mismatch"]][["Invoice ID", "Quantity", "Unit Price", "Sales_Calc", "Sales"]]
            .rename(columns={"Sales_Calc": "Recalculated", "Sales": "Original"})
            .head(20),
            use_container_width=True,
        )

    # Data type check
    st.markdown("#### Data Types")
    dtype_df = pd.DataFrame({
        "Column": df.columns,
        "dtype": df.dtypes.astype(str).values,
        "Non-Null Count": df.notnull().sum().values,
        "Unique Values": df.nunique().values,
    })
    st.dataframe(dtype_df, hide_index=True, use_container_width=True)

    if total_missing == 0 and qr["duplicates"] == 0 and qr["neg_qty"] == 0 and qr["neg_price"] == 0:
        insight("Dataset is clean — no missing values, duplicates, or invalid numeric entries detected.")
    else:
        warn("One or more data quality issues were found. Review the table above before drawing conclusions.")

# ═══════════════════════════════════════════════════════════
# TAB 2 — SALES SUMMARY
# ═══════════════════════════════════════════════════════════
with tabs[2]:
    section("📊 Overall Sales Summary")

    total_sales = fdf["Sales"].sum()
    total_qty = fdf["Quantity"].sum()
    avg_sale = fdf["Sales"].mean()
    avg_rating = fdf["Rating"].mean()
    total_txn = len(fdf)
    avg_basket = total_sales / total_txn if total_txn else 0

    cols = st.columns(3)
    cards = [
        ("Total Revenue", fmt_inr(total_sales), f"{total_txn:,} transactions"),
        ("Total Units Sold", f"{total_qty:,}", "across all categories"),
        ("Avg Transaction Value", fmt_inr(avg_basket), "revenue per invoice"),
        ("Avg Sale per Row", fmt_inr(avg_sale), "mean of all line items"),
        ("Avg Customer Rating", f"{avg_rating:.2f} / 5", "satisfaction score"),
        ("Unique Products", str(fdf["Product"].nunique()), "distinct SKUs"),
    ]
    for i, (lbl, val, sub) in enumerate(cards):
        with cols[i % 3]:
            st.markdown(metric_card(lbl, val, sub), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

    # Summary by Category
    st.markdown("#### Revenue Summary by Category")
    cat_sum = (
        fdf.groupby("Category")
        .agg(Total_Revenue=("Sales", "sum"),
             Total_Qty=("Quantity", "sum"),
             Avg_Sale=("Sales", "mean"),
             Transactions=("Invoice ID", "count"),
             Avg_Rating=("Rating", "mean"))
        .sort_values("Total_Revenue", ascending=False)
        .reset_index()
    )
    cat_sum["Avg_Sale"] = cat_sum["Avg_Sale"].round(2)
    cat_sum["Avg_Rating"] = cat_sum["Avg_Rating"].round(2)
    st.dataframe(
        cat_sum.style.format({
            "Total_Revenue": "₹{:,.2f}",
            "Avg_Sale": "₹{:,.2f}",
            "Total_Qty": "{:,}",
            "Avg_Rating": "{:.2f}",
        }),
        hide_index=True, use_container_width=True,
    )

    # Summary by City
    st.markdown("#### Revenue Summary by City")
    city_sum = (
        fdf.groupby("City")
        .agg(Total_Revenue=("Sales", "sum"),
             Transactions=("Invoice ID", "count"),
             Avg_Sale=("Sales", "mean"),
             Avg_Rating=("Rating", "mean"))
        .sort_values("Total_Revenue", ascending=False)
        .reset_index()
    )
    st.dataframe(
        city_sum.style.format({
            "Total_Revenue": "₹{:,.2f}",
            "Avg_Sale": "₹{:,.2f}",
            "Avg_Rating": "{:.2f}",
        }),
        hide_index=True, use_container_width=True,
    )

# ═══════════════════════════════════════════════════════════
# TAB 3 — TREND ANALYSIS
# ═══════════════════════════════════════════════════════════
with tabs[3]:
    section("📈 Sales Trend Over Time")

    monthly = (
        fdf.groupby("Month_dt")
        .agg(Revenue=("Sales", "sum"), Transactions=("Invoice ID", "count"))
        .reset_index()
        .sort_values("Month_dt")
    )

    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    fig.patch.set_facecolor("#ffffff")

    axes[0].bar(monthly["Month_dt"].astype(str), monthly["Revenue"],
                color=PALETTE[0], edgecolor="white", linewidth=0.5)
    axes[0].set_title("Monthly Revenue (₹)", fontsize=13, fontweight="bold", pad=8)
    axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    axes[0].set_facecolor("#f7f8fa")
    axes[0].grid(axis="y", linestyle="--", alpha=0.5)

    axes[1].plot(monthly["Month_dt"].astype(str), monthly["Transactions"],
                 marker="o", color=PALETTE[1], linewidth=2, markersize=6)
    axes[1].fill_between(range(len(monthly)), monthly["Transactions"],
                          alpha=0.12, color=PALETTE[1])
    axes[1].set_title("Monthly Transaction Count", fontsize=13, fontweight="bold", pad=8)
    axes[1].set_facecolor("#f7f8fa")
    axes[1].grid(axis="y", linestyle="--", alpha=0.5)
    axes[1].tick_params(axis="x", rotation=45)

    plt.tight_layout(pad=2)
    st.pyplot(fig)
    plt.close(fig)

    # Day-of-week pattern
    st.markdown("#### Sales by Day of Week")
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow = (
        fdf.groupby("DayOfWeek")["Sales"]
        .sum()
        .reindex(dow_order)
        .dropna()
        .reset_index()
    )

    fig2, ax2 = plt.subplots(figsize=(10, 4))
    fig2.patch.set_facecolor("#ffffff")
    bars = ax2.bar(dow["DayOfWeek"], dow["Sales"], color=PALETTE[2], edgecolor="white")
    ax2.set_title("Total Revenue by Day of Week", fontsize=13, fontweight="bold")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    ax2.set_facecolor("#f7f8fa")
    ax2.grid(axis="y", linestyle="--", alpha=0.5)
    ax2.tick_params(axis="x", rotation=20)
    for bar in bars:
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 200,
                 f"₹{bar.get_height():,.0f}", ha="center", va="bottom", fontsize=8, color="#57606a")
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

    peak_day = dow.loc[dow["Sales"].idxmax(), "DayOfWeek"]
    peak_rev = dow["Sales"].max()
    insight(f"Peak sales day is **{peak_day}** with ₹{peak_rev:,.2f} in revenue.")

# ═══════════════════════════════════════════════════════════
# TAB 4 — CATEGORY & PRODUCT
# ═══════════════════════════════════════════════════════════
with tabs[4]:
    section("🗂️ Category & Product Performance")

    col_l, col_r = st.columns(2)

    # Category revenue bar chart
    cat_rev = (
        fdf.groupby("Category")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    with col_l:
        fig, ax = plt.subplots(figsize=(6, 5))
        fig.patch.set_facecolor("#ffffff")
        colors = PALETTE[:len(cat_rev)]
        bars = ax.barh(cat_rev["Category"][::-1], cat_rev["Sales"][::-1],
                       color=colors[::-1], edgecolor="white")
        ax.set_title("Revenue by Category", fontsize=13, fontweight="bold")
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
        ax.set_facecolor("#f7f8fa")
        ax.grid(axis="x", linestyle="--", alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # Category share pie chart
    with col_r:
        fig2, ax2 = plt.subplots(figsize=(6, 5))
        fig2.patch.set_facecolor("#ffffff")
        wedges, texts, autotexts = ax2.pie(
            cat_rev["Sales"], labels=cat_rev["Category"],
            autopct="%1.1f%%", colors=PALETTE[:len(cat_rev)],
            startangle=140, pctdistance=0.78,
            wedgeprops=dict(edgecolor="white", linewidth=1.5),
        )
        for t in autotexts:
            t.set_fontsize(9)
        ax2.set_title("Category Revenue Share", fontsize=13, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

    # Top 10 products
    st.markdown("#### Top 10 Products by Revenue")
    prod_rev = (
        fdf.groupby("Product")
        .agg(Revenue=("Sales", "sum"), Units=("Quantity", "sum"), Transactions=("Invoice ID", "count"))
        .sort_values("Revenue", ascending=False)
        .head(10)
        .reset_index()
    )
    fig3, ax3 = plt.subplots(figsize=(12, 4))
    fig3.patch.set_facecolor("#ffffff")
    ax3.bar(prod_rev["Product"], prod_rev["Revenue"],
            color=PALETTE[0], edgecolor="white")
    ax3.set_title("Top 10 Products by Revenue", fontsize=13, fontweight="bold")
    ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    ax3.set_facecolor("#f7f8fa")
    ax3.grid(axis="y", linestyle="--", alpha=0.5)
    ax3.tick_params(axis="x", rotation=30)
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close(fig3)

    st.dataframe(
        prod_rev.style.format({"Revenue": "₹{:,.2f}", "Units": "{:,}"}),
        hide_index=True, use_container_width=True,
    )

    top_cat = cat_rev.iloc[0]["Category"]
    top_cat_rev = cat_rev.iloc[0]["Sales"]
    insight(f"**{top_cat}** is the highest-revenue category at ₹{top_cat_rev:,.2f}.")

# ═══════════════════════════════════════════════════════════
# TAB 5 — CITY & BRANCH
# ═══════════════════════════════════════════════════════════
with tabs[5]:
    section("🏙️ City & Branch Performance")

    city_rev = (
        fdf.groupby("City")
        .agg(Revenue=("Sales", "sum"), Transactions=("Invoice ID", "count"),
             Avg_Rating=("Rating", "mean"), Units=("Quantity", "sum"))
        .sort_values("Revenue", ascending=False)
        .reset_index()
    )

    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor("#ffffff")
        ax.bar(city_rev["City"], city_rev["Revenue"],
               color=PALETTE[:len(city_rev)], edgecolor="white")
        ax.set_title("Total Revenue by City", fontsize=13, fontweight="bold")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
        ax.set_facecolor("#f7f8fa")
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        for bar in ax.patches:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 100,
                    f"₹{bar.get_height():,.0f}", ha="center", va="bottom",
                    fontsize=8, color="#57606a")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        fig2.patch.set_facecolor("#ffffff")
        ax2.bar(city_rev["City"], city_rev["Avg_Rating"],
                color=PALETTE[3], edgecolor="white")
        ax2.set_title("Avg Customer Rating by City", fontsize=13, fontweight="bold")
        ax2.set_ylim(0, 5)
        ax2.axhline(city_rev["Avg_Rating"].mean(), color="#ef4444",
                    linestyle="--", linewidth=1.2, label=f"Overall avg {city_rev['Avg_Rating'].mean():.2f}")
        ax2.legend(fontsize=9)
        ax2.set_facecolor("#f7f8fa")
        ax2.grid(axis="y", linestyle="--", alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

    # Branch breakdown
    st.markdown("#### Branch Summary")
    branch_rev = (
        fdf.groupby(["Branch", "City"])
        .agg(Revenue=("Sales", "sum"), Transactions=("Invoice ID", "count"),
             Avg_Rating=("Rating", "mean"))
        .sort_values("Revenue", ascending=False)
        .reset_index()
    )
    st.dataframe(
        branch_rev.style.format({"Revenue": "₹{:,.2f}", "Avg_Rating": "{:.2f}"}),
        hide_index=True, use_container_width=True,
    )

    top_city = city_rev.iloc[0]["City"]
    top_city_rev = city_rev.iloc[0]["Revenue"]
    insight(f"**{top_city}** leads all cities with ₹{top_city_rev:,.2f} in total revenue.")

# ═══════════════════════════════════════════════════════════
# TAB 6 — CUSTOMER INSIGHTS
# ═══════════════════════════════════════════════════════════
with tabs[6]:
    section("👥 Customer Insights")

    col1, col2 = st.columns(2)

    # Customer Type
    ctype = (
        fdf.groupby("Customer Type")
        .agg(Revenue=("Sales", "sum"), Transactions=("Invoice ID", "count"),
             Avg_Basket=("Sales", "mean"), Avg_Rating=("Rating", "mean"))
        .reset_index()
    )
    with col1:
        fig, ax = plt.subplots(figsize=(5, 4))
        fig.patch.set_facecolor("#ffffff")
        ax.bar(ctype["Customer Type"], ctype["Revenue"],
               color=[PALETTE[0], PALETTE[1]], edgecolor="white", width=0.5)
        ax.set_title("Revenue: Member vs Normal", fontsize=12, fontweight="bold")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
        ax.set_facecolor("#f7f8fa")
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        fig2.patch.set_facecolor("#ffffff")
        ax2.bar(ctype["Customer Type"], ctype["Avg_Basket"],
                color=[PALETTE[2], PALETTE[3]], edgecolor="white", width=0.5)
        ax2.set_title("Avg Basket Size: Member vs Normal", fontsize=12, fontweight="bold")
        ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
        ax2.set_facecolor("#f7f8fa")
        ax2.grid(axis="y", linestyle="--", alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

    # Gender breakdown
    st.markdown("#### Revenue & Rating by Gender")
    gender = (
        fdf.groupby("Gender")
        .agg(Revenue=("Sales", "sum"), Transactions=("Invoice ID", "count"),
             Avg_Rating=("Rating", "mean"))
        .reset_index()
    )
    col3, col4 = st.columns(2)
    with col3:
        fig3, ax3 = plt.subplots(figsize=(5, 4))
        fig3.patch.set_facecolor("#ffffff")
        ax3.pie(gender["Revenue"], labels=gender["Gender"],
                autopct="%1.1f%%", colors=[PALETTE[0], PALETTE[4]],
                startangle=90, wedgeprops=dict(edgecolor="white", linewidth=2))
        ax3.set_title("Revenue Share by Gender", fontsize=12, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)

    with col4:
        # Heatmap: Category × Gender avg sales
        heat = fdf.pivot_table(values="Sales", index="Category",
                               columns="Gender", aggfunc="mean").fillna(0)
        fig4, ax4 = plt.subplots(figsize=(5, 4))
        fig4.patch.set_facecolor("#ffffff")
        sns.heatmap(heat, annot=True, fmt=".0f", cmap="Blues",
                    linewidths=0.5, ax=ax4, cbar_kws={"format": "₹%.0f"})
        ax4.set_title("Avg Sales: Category × Gender (₹)", fontsize=11, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig4)
        plt.close(fig4)

    st.dataframe(
        ctype.style.format({"Revenue": "₹{:,.2f}", "Avg_Basket": "₹{:,.2f}", "Avg_Rating": "{:.2f}"}),
        hide_index=True, use_container_width=True,
    )

    top_type = ctype.sort_values("Revenue", ascending=False).iloc[0]["Customer Type"]
    insight(f"**{top_type}** customers generate higher total revenue — loyalty programmes may amplify this further.")

# ═══════════════════════════════════════════════════════════
# TAB 7 — PAYMENT ANALYSIS
# ═══════════════════════════════════════════════════════════
with tabs[7]:
    section("💳 Payment Method Analysis")

    pay = (
        fdf.groupby("Payment")
        .agg(Revenue=("Sales", "sum"), Transactions=("Invoice ID", "count"),
             Avg_Sale=("Sales", "mean"))
        .sort_values("Revenue", ascending=False)
        .reset_index()
    )

    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots(figsize=(6, 5))
        fig.patch.set_facecolor("#ffffff")
        ax.bar(pay["Payment"], pay["Revenue"],
               color=PALETTE[:len(pay)], edgecolor="white")
        ax.set_title("Revenue by Payment Method", fontsize=13, fontweight="bold")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
        ax.set_facecolor("#f7f8fa")
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.tick_params(axis="x", rotation=15)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        fig2, ax2 = plt.subplots(figsize=(6, 5))
        fig2.patch.set_facecolor("#ffffff")
        ax2.pie(pay["Transactions"], labels=pay["Payment"],
                autopct="%1.1f%%", colors=PALETTE[:len(pay)],
                startangle=120, wedgeprops=dict(edgecolor="white", linewidth=2))
        ax2.set_title("Transaction Count by Payment", fontsize=13, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

    st.dataframe(
        pay.style.format({"Revenue": "₹{:,.2f}", "Avg_Sale": "₹{:,.2f}"}),
        hide_index=True, use_container_width=True,
    )

    top_pay = pay.iloc[0]["Payment"]
    insight(f"**{top_pay}** is the most popular payment method by revenue.")

# ═══════════════════════════════════════════════════════════
# TAB 8 — BUSINESS DECISIONS
# ═══════════════════════════════════════════════════════════
with tabs[8]:
    section("💡 Data-Driven Business Decisions")

    # Recompute key stats for the full dataset (unfiltered for strategic view)
    full = df.copy()

    top_cat_full = full.groupby("Category")["Sales"].sum().idxmax()
    bot_cat_full = full.groupby("Category")["Sales"].sum().idxmin()
    top_city_full = full.groupby("City")["Sales"].sum().idxmax()
    bot_city_full = full.groupby("City")["Sales"].sum().idxmin()
    top_pay_full = full.groupby("Payment")["Sales"].sum().idxmax()
    member_rev = full[full["Customer Type"] == "Member"]["Sales"].sum()
    normal_rev = full[full["Customer Type"] == "Normal"]["Sales"].sum()
    low_rating_cats = full.groupby("Category")["Rating"].mean()
    lowest_rated = low_rating_cats.idxmin()
    highest_rated = low_rating_cats.idxmax()
    peak_day_full = full.groupby("DayOfWeek")["Sales"].sum().idxmax()
    peak_month_full = full.groupby("Month")["Sales"].sum().idxmax()

    decisions = [
        ("📦 Expand Top Categories",
         f"<b>{top_cat_full}</b> is the best-performing category. Increase SKU variety, "
         f"negotiate better supplier terms, and allocate prime shelf space to maximise revenue."),
        ("📉 Revive Underperforming Categories",
         f"<b>{bot_cat_full}</b> generates the least revenue. Investigate pricing, placement, "
         f"and promotion strategies. Consider bundling with high-demand categories."),
        ("🏙️ Focus Investment in Top City",
         f"<b>{top_city_full}</b> leads in revenue. Prioritise it for new product launches, "
         f"exclusive offers, and enhanced in-store experience to consolidate market share."),
        ("📈 Grow Underperforming City",
         f"<b>{bot_city_full}</b> has the lowest revenue. Targeted local marketing campaigns "
         f"and personalised discounts can unlock growth in this untapped market."),
        ("💳 Promote Preferred Payment",
         f"Customers prefer <b>{top_pay_full}</b> for payments. Partner with payment providers "
         f"to offer cashback or rewards for this channel to increase conversion rates."),
        ("🎟️ Strengthen Loyalty Programme",
         f"Members contribute ₹{member_rev:,.2f} vs ₹{normal_rev:,.2f} from Normal customers. "
         f"Convert Normal customers to Members with sign-up incentives; Members tend to spend more per visit."),
        ("⭐ Improve Low-Rated Categories",
         f"<b>{lowest_rated}</b> has the lowest average customer rating. Investigate product quality, "
         f"freshness, and variety. High ratings in <b>{highest_rated}</b> show what good looks like."),
        ("📅 Plan Promotions Around Peak Periods",
         f"Peak sales occur on <b>{peak_day_full}s</b> (day) and in <b>{peak_month_full}</b> (month). "
         f"Schedule major promotions, flash sales, and increased staff deployment during these windows."),
        ("📊 Monitor Basket Size",
         f"Average transaction value provides a strong lever for growth. Introduce upselling prompts, "
         f"combo offers, and quantity discounts to increase items per transaction."),
        ("🔄 Data-Driven Restocking",
         f"High-volume products identified in the Category & Product tab should be stocked ahead of "
         f"peak days and months to avoid stock-outs and lost sales."),
    ]

    for title, body in decisions:
        st.markdown(
            f'<div class="insight-card"><b>{title}</b><br>{body}</div>',
            unsafe_allow_html=True,
        )

    # Summary heatmap: City × Category revenue
    st.markdown("---")
    st.markdown("#### Revenue Heatmap — City × Category")
    hmap = df.pivot_table(values="Sales", index="City", columns="Category", aggfunc="sum").fillna(0)
    fig, ax = plt.subplots(figsize=(12, 4))
    fig.patch.set_facecolor("#ffffff")
    sns.heatmap(hmap, annot=True, fmt=".0f", cmap="YlOrRd",
                linewidths=0.5, ax=ax, cbar_kws={"format": "₹%.0f"})
    ax.set_title("Total Revenue (₹) — City × Category", fontsize=13, fontweight="bold")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    insight(
        "Use the City × Category heatmap to pinpoint which product categories are underperforming "
        "in specific cities and direct targeted campaigns accordingly."
    )

# ──────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; font-size:12px; color:#57606a;'>"
    "IBM SkillsBuild · Data Analytics with AI Internship 2026 · "
    "Supermarket Sales Analysis Dashboard · Built with Streamlit"
    "</p>",
    unsafe_allow_html=True,
)
