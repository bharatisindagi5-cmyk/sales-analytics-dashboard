# Sales Analytics Dashboard

An interactive Dash/Plotly dashboard for exploring the Kaggle **Superstore Sales** dataset.

## Project structure

```
sales_analytics_dashboard/
├── app.py                 # Main Dash application
├── requirements.txt       # Python dependencies
├── data/
│   └── Sample - Superstore.csv   # <- put your downloaded dataset here
└── assets/
    └── style.css           # Dashboard styling (auto-loaded by Dash)
```

## Setup

1. You've already installed pandas — now install the remaining dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Put your downloaded CSV inside the `data/` folder and make sure the filename
   matches `Sample - Superstore.csv`, OR set an environment variable pointing
   to your file:
   ```bash
   export SALES_DATA_PATH="/path/to/your/file.csv"   # Windows: set SALES_DATA_PATH=...
   ```

3. Run the app:
   ```bash
   python app.py
   ```

4. Open your browser at **http://127.0.0.1:8050**

## Features

- **Filters**: Region, Category, and Order Date range
- **KPI cards**: Total Sales, Total Profit, Order Count, Avg. Discount
- **Charts**:
  - Monthly sales trend (line chart)
  - Sales by category (donut chart)
  - Sales by region (bar chart)
  - Top 10 products by sales (bar chart)
  - Profit vs. Sales scatter plot (colored by category)

All charts and KPIs update live based on the selected filters.

## Notes on the dataset

The Superstore CSV is typically encoded in `latin-1` (not UTF-8) and uses
these standard columns: `Order ID, Order Date, Ship Date, Ship Mode,
Customer ID, Customer Name, Segment, Country, City, State, Postal Code,
Region, Product ID, Category, Sub-Category, Product Name, Sales, Quantity,
Discount, Profit`.

If your column names differ slightly (e.g. extra spaces), `app.py` already
strips whitespace from column headers — but if names are substantially
different, adjust the column references in `app.py` accordingly.

## Next steps / ideas to extend

- Add a US choropleth map of sales by state (`px.choropleth`)
- Add a "Segment" filter (Consumer / Corporate / Home Office)
- Export filtered data as CSV via a download button
- Deploy with `gunicorn` + Render/Heroku for a shareable link
