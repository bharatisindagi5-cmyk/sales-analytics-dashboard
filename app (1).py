"""
Sales Analytics Dashboard
--------------------------
Interactive Dash/Plotly dashboard for the Kaggle "Superstore Sales" dataset.

Expected dataset columns (standard Superstore schema):
    Row ID, Order ID, Order Date, Ship Date, Ship Mode, Customer ID, Customer Name,
    Segment, Country, City, State, Postal Code, Region, Product ID,
    Category, Sub-Category, Product Name, Sales, Quantity, Discount, Profit

Run:
    python app.py
Then open http://127.0.0.1:8050 in your browser.
"""

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import os

# ---------------------------------------------------------------------------
# 1. LOAD & CLEAN DATA
# ---------------------------------------------------------------------------
DATA_PATH = os.environ.get("SALES_DATA_PATH", "Sample - Superstore.csv")

def load_data(path: str) -> pd.DataFrame:
    # Superstore CSV is usually encoded in latin-1, not utf-8
    df = pd.read_csv(path, encoding="latin1")

    # Normalize column names (strip spaces) just in case
    df.columns = [c.strip() for c in df.columns]

    # Parse dates
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors="coerce")

    # Drop rows with no order date / sales
    df = df.dropna(subset=["Order Date", "Sales"])

    # Helper columns for aggregation
    df["Order Year"] = df["Order Date"].dt.year
    df["Order Month"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()

    return df

df = load_data(DATA_PATH)

regions = sorted(df["Region"].dropna().unique())
categories = sorted(df["Category"].dropna().unique())
min_date, max_date = df["Order Date"].min(), df["Order Date"].max()

# ---------------------------------------------------------------------------
# 2. APP LAYOUT
# ---------------------------------------------------------------------------
app = Dash(__name__)
app.title = "Sales Analytics Dashboard"

def kpi_card(title, value_id):
    return html.Div(
        className="kpi-card",
        children=[
            html.H4(title, className="kpi-title"),
            html.H2(id=value_id, className="kpi-value"),
        ],
    )

app.layout = html.Div(
    className="app-container",
    children=[
        html.Div(
            className="header",
            children=[
                html.H1("Sales Analytics Dashboard"),
                html.P("Superstore performance overview — sales, profit, and trends"),
            ],
        ),

        # ---- Filters ----
        html.Div(
            className="filters",
            children=[
                html.Div(
                    [
                        html.Label("Region"),
                        dcc.Dropdown(
                            id="region-filter",
                            options=[{"label": r, "value": r} for r in regions],
                            value=[],
                            multi=True,
                            placeholder="All regions",
                        ),
                    ],
                    className="filter-item",
                ),
                html.Div(
                    [
                        html.Label("Category"),
                        dcc.Dropdown(
                            id="category-filter",
                            options=[{"label": c, "value": c} for c in categories],
                            value=[],
                            multi=True,
                            placeholder="All categories",
                        ),
                    ],
                    className="filter-item",
                ),
                html.Div(
                    [
                        html.Label("Order Date Range"),
                        dcc.DatePickerRange(
                            id="date-filter",
                            min_date_allowed=min_date,
                            max_date_allowed=max_date,
                            start_date=min_date,
                            end_date=max_date,
                        ),
                    ],
                    className="filter-item",
                ),
            ],
        ),

        # ---- KPI Row ----
        html.Div(
            className="kpi-row",
            children=[
                kpi_card("Total Sales", "kpi-sales"),
                kpi_card("Total Profit", "kpi-profit"),
                kpi_card("Orders", "kpi-orders"),
                kpi_card("Avg Discount", "kpi-discount"),
            ],
        ),

        # ---- Charts ----
        html.Div(
            className="charts-row",
            children=[
                dcc.Graph(id="sales-trend-chart", className="chart-half"),
                dcc.Graph(id="category-sales-chart", className="chart-half"),
            ],
        ),
        html.Div(
            className="charts-row",
            children=[
                dcc.Graph(id="region-sales-chart", className="chart-half"),
                dcc.Graph(id="top-products-chart", className="chart-half"),
            ],
        ),
        html.Div(
            className="charts-row",
            children=[
                dcc.Graph(id="profit-sales-scatter", className="chart-full"),
            ],
        ),
    ],
)

# ---------------------------------------------------------------------------
# 3. CALLBACKS
# ---------------------------------------------------------------------------
@app.callback(
    Output("kpi-sales", "children"),
    Output("kpi-profit", "children"),
    Output("kpi-orders", "children"),
    Output("kpi-discount", "children"),
    Output("sales-trend-chart", "figure"),
    Output("category-sales-chart", "figure"),
    Output("region-sales-chart", "figure"),
    Output("top-products-chart", "figure"),
    Output("profit-sales-scatter", "figure"),
    Input("region-filter", "value"),
    Input("category-filter", "value"),
    Input("date-filter", "start_date"),
    Input("date-filter", "end_date"),
)
def update_dashboard(selected_regions, selected_categories, start_date, end_date):
    dff = df.copy()

    if selected_regions:
        dff = dff[dff["Region"].isin(selected_regions)]
    if selected_categories:
        dff = dff[dff["Category"].isin(selected_categories)]
    if start_date and end_date:
        dff = dff[(dff["Order Date"] >= start_date) & (dff["Order Date"] <= end_date)]

    # ---- KPIs ----
    total_sales = f"${dff['Sales'].sum():,.0f}"
    total_profit = f"${dff['Profit'].sum():,.0f}"
    total_orders = f"{dff['Order ID'].nunique():,}"
    avg_discount = f"{dff['Discount'].mean() * 100:,.1f}%" if len(dff) else "0%"

    # ---- Sales trend over time (monthly) ----
    trend = dff.groupby("Order Month", as_index=False)["Sales"].sum()
    fig_trend = px.line(
        trend, x="Order Month", y="Sales", title="Monthly Sales Trend", markers=True
    )
    fig_trend.update_layout(margin=dict(l=20, r=20, t=50, b=20))

    # ---- Sales by category ----
    cat_sales = dff.groupby("Category", as_index=False)["Sales"].sum()
    fig_category = px.pie(
        cat_sales, names="Category", values="Sales", title="Sales by Category", hole=0.4
    )
    fig_category.update_layout(margin=dict(l=20, r=20, t=50, b=20))

    # ---- Sales by region ----
    reg_sales = dff.groupby("Region", as_index=False)["Sales"].sum().sort_values("Sales")
    fig_region = px.bar(
        reg_sales, x="Sales", y="Region", orientation="h", title="Sales by Region"
    )
    fig_region.update_layout(margin=dict(l=20, r=20, t=50, b=20))

    # ---- Top 10 products by sales ----
    top_products = (
        dff.groupby("Product Name", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
        .head(10)
    )
    fig_top_products = px.bar(
        top_products.sort_values("Sales"),
        x="Sales",
        y="Product Name",
        orientation="h",
        title="Top 10 Products by Sales",
    )
    fig_top_products.update_layout(margin=dict(l=20, r=20, t=50, b=20))

    # ---- Profit vs Sales scatter (by sub-category) ----
    fig_scatter = px.scatter(
        dff,
        x="Sales",
        y="Profit",
        color="Category",
        hover_data=["Sub-Category", "Product Name"],
        title="Profit vs Sales (per order line)",
        opacity=0.6,
    )
    fig_scatter.update_layout(margin=dict(l=20, r=20, t=50, b=20))

    return (
        total_sales,
        total_profit,
        total_orders,
        avg_discount,
        fig_trend,
        fig_category,
        fig_region,
        fig_top_products,
        fig_scatter,
    )


if __name__ == "__main__":
    app.run(debug=True)