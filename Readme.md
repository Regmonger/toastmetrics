# ToastMetrics

A sales analysis tool for Toast POS data exports.

## Purpose

Analyze menu performance from Toast POS CSV exports to identify:
- Top selling items by quantity and revenue
- Poor performers (candidates for menu review)
- Category-specific breakdowns

## Features

- Load and normalize Toast menu-breakdown CSV files
- Store data in SQLite for SQL analysis
- Generate reports: top sellers, revenue leaders, poor performers
- Query data using SQL

## Usage
```python
python toastmetrics_app.py
```

## Sample Output

- Top 10 sellers by quantity
- Top 10 items by revenue  
- Bottom 10 poor performers
- Bottom 10 food items specifically
- SQL query results

## Technologies

- Python
- pandas (data manipulation)
- SQLite (data storage and SQL queries)

## Data Source

Menu breakdown exports from Toast POS system.