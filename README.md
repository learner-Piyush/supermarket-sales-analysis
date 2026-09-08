# 🛒 Supermarket Sales Analysis

A data analytics project built for the **IBM SkillsBuild Data Analytics with AI Internship 2026** that analyses 500 supermarket transactions across 4 Indian cities using Python and an interactive Streamlit dashboard.

---

## 📋 Project Overview

| Item | Detail |
|------|--------|
| **Dataset** | `supermarket_sales_500_rows.csv` |
| **Records** | 500 transactions |
| **Date Range** | January – July 2026 |
| **Cities** | Mumbai · Delhi · Bengaluru · Jaipur |
| **Categories** | 8 product categories · 20 unique SKUs |

### Objectives

1. Collect and load the CSV dataset
2. Check data for missing or incorrect values
3. Calculate `Sales = Quantity × Unit Price`
4. Group and summarise data using totals, counts, and averages
5. Create charts to compare results
6. Use results to make data-driven business decisions

---

## 🗂️ Project Structure

```
.
├── supermarket_sales_app.py          # Main Streamlit dashboard application
├── supermarket_sales_500_rows.csv    # Source dataset
├── Supermarket_Sales_Report.pptx     # PowerPoint presentation report
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- pip

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd <repo-folder>

# 2. (Recommended) Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt
```

> **Windows users:** If you encounter a `DLL load failed` error for `pyarrow`, ensure you are using `pandas==2.2.3` as pinned in `requirements.txt`. Do **not** upgrade pandas to 3.x on systems with Application Control policies enabled.

### Run the Dashboard

```bash
streamlit run supermarket_sales_app.py
```

The app opens at **http://localhost:8501** in your default browser.

---

## 📊 Dashboard Tabs

| Tab | Contents |
|-----|----------|
| 📋 **Data Overview** | Column reference, sample rows, statistical summary |
| 🔬 **Data Quality** | Missing values, duplicates, negative value checks, Sales recalculation verification |
| 📊 **Sales Summary** | 6 KPI metric cards, revenue tables by category and city |
| 📈 **Trend Analysis** | Monthly revenue bar chart, transaction trend line, day-of-week pattern |
| 🗂️ **Category & Product** | Revenue bar + pie charts, Top-10 product ranking |
| 🏙️ **City & Branch** | City revenue comparison, avg rating chart, branch detail table |
| 👥 **Customer Insights** | Member vs Normal, gender split, Category × Gender heatmap |
| 💳 **Payment Analysis** | Revenue and transaction share by payment method |
| 💡 **Business Decisions** | 10 data-driven recommendations, City × Category revenue heatmap |

### Sidebar Filters

All charts and tables respond live to these filters:

- **City** — filter by one or more cities
- **Category** — filter by product category
- **Customer Type** — Member or Normal
- **Payment Method** — UPI / Card / Cash / Net Banking
- **Date Range** — pick a custom start and end date

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `streamlit` | ≥ 1.35.0 | Web dashboard framework |
| `pandas` | == 2.2.3 | Data loading, cleaning, aggregation |
| `numpy` | ≥ 1.24.0 | Numerical operations |
| `matplotlib` | ≥ 3.7.0 | Static charts and bar plots |
| `seaborn` | ≥ 0.12.0 | Heatmaps and statistical plots |

---

## 📁 Dataset Schema

| Column | Type | Description |
|--------|------|-------------|
| `Invoice ID` | string | Unique transaction identifier |
| `Date` | date | Transaction date |
| `Branch` | string | Store branch code (A / B / C / D) |
| `City` | string | City of the branch |
| `Customer Type` | string | Member or Normal |
| `Gender` | string | Male or Female |
| `Product` | string | Product name (20 unique SKUs) |
| `Category` | string | Product category (8 categories) |
| `Quantity` | int | Units purchased |
| `Unit Price` | float | Price per unit (₹) |
| `Payment` | string | UPI / Card / Cash / Net Banking |
| `Rating` | float | Customer satisfaction score (0–5) |
| `Sales` | float | Derived: `Quantity × Unit Price` (₹) |

---

## 📈 Key Findings

| Metric | Value |
|--------|-------|
| Total Revenue | ₹2,44,411.08 |
| Total Transactions | 500 |
| Total Units Sold | 2,768 |
| Avg Transaction Value | ₹488.82 |
| Avg Customer Rating | 3.99 / 5.0 |
| Top Category | Beverages (₹56,108) |
| Top City | Mumbai (₹72,469) |
| Peak Month | April 2026 (₹52,570) |
| Peak Day | Monday (₹42,602) |
| Top Payment Method | UPI (27.8% share) |

---

## 📄 Report

A fully formatted PowerPoint presentation (`Supermarket_Sales_Report.pptx`) is included with 11 slides covering all analytical steps, data tables, visualisations, and business recommendations. Every slide includes speaker notes.

---

## 🏢 Internship

**IBM SkillsBuild — Data Analytics with AI Internship 2026**  
Business Solutions with IBM Bob
