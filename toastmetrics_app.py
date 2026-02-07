#=======================================================
#            ToastMetrics Application
#=======================================================

import os
import pandas as pd
import sqlite3


def find_menu_csvs_in_folder(folder_path):
    """Return all menu-breakdown CSVs inside a folder."""
    hits = []
    for file in os.listdir(folder_path):
        f = file.lower()
        if "menu-breakdown" in f and f.endswith(".csv"):
            hits.append(os.path.join(folder_path, file))
    return hits


def find_week_folders(base_path):
    """Subfolders under base_path."""
    return [
        os.path.join(base_path, name)
        for name in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, name))
    ]


# convert to string
# strip commas and $
# then to_numeric
def normalize_menu_df(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize menu-breakdown DataFrame columns."""
    df.columns = df.columns.str.strip()
    num_cols = ["Avg Price", "Quantity", "Gross Sales", "Discount Amount", "Net Sales"]
    for col in num_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", "").str.replace("$", "")
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def load_all_weeks(base_path):
    """Load all menu-breakdown CSVs from week subfolders."""
    
    all_dfs = []

    # Load any menu-breakdown CSVs directly in base_path
    for csv_path in find_menu_csvs_in_folder(base_path):
        df = pd.read_csv(csv_path)
        df = normalize_menu_df(df)
        df["Week"] = os.path.splitext(os.path.basename(csv_path))[0]  # filename as label
        all_dfs.append(df)

    if not all_dfs:
        return pd.DataFrame()

    return pd.concat(all_dfs, ignore_index=True)


# Top n items by quantity sold
def top_items_by_quantity(df, n=10):
    """Return top n items by quantity sold."""
    return (
        df.groupby("Item Name", as_index=False)["Quantity"]
          .sum()
          .sort_values("Quantity", ascending=False)
          .head(n)
    )


# Top n items by revenue (Net Sales)
def top_items_by_revenue(df, n=10):
    """Return top n items by net sales revenue."""
    return (
        df.groupby("Item Name", as_index=False)["Net Sales"]
          .sum()
          .sort_values("Net Sales", ascending=False)
          .head(n)
    )


def save_to_database(df, db_path="Projects\\ToastMetrics\\toastmetrics.db"):
    """Save DataFrame to SQLite database."""
    conn = sqlite3.connect(db_path)
    df.to_sql("sales", conn, if_exists="replace", index=False)
    conn.close()
    print(f"Data saved to {db_path}")


def bottom_items_by_quantity(df, n=10):
    """Return bottom n items by quantity sold (poor performers)."""
    return (
        df.groupby("Item Name", as_index=False)["Quantity"]
          .sum()
          .sort_values("Quantity", ascending=True)
          .head(n)
    )


def bottom_items_by_category(df, category="Food", n=10):
    """Return bottom n items by quantity for a specific category."""
    filtered = df[df["Sales Category"] == category]
    return (
        filtered.groupby("Item Name", as_index=False)["Quantity"]
          .sum()
          .sort_values("Quantity", ascending=True)
          .head(n)
    )


def query_database(query, db_path="toastmetrics.db"):
    """Run a SQL query and return results as DataFrame."""
    conn = sqlite3.connect(db_path)
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result


if __name__ == "__main__":
    base = os.path.join("Projects", "ToastMetrics", "ToastMetrics_data", "2025-12")
    df = load_all_weeks(base)
    
    if df.empty:
        print("No data loaded - check folder path / file names.")
        raise SystemExit
    
    # Filter out totals
    item_df = df[~df["Item Name"].str.contains("total", case=False, na=False)]
    
    # Save to database
    save_to_database(item_df)
    
    # Reports
    print("\n=== TOP 10 SELLERS (by quantity) ===")
    print(top_items_by_quantity(item_df))
    
    print("\n=== TOP 10 BY REVENUE ===")
    print(top_items_by_revenue(item_df))
    
    print("\n=== BOTTOM 10 (poor performers) ===")
    print(bottom_items_by_quantity(item_df))

    print("\n=== BOTTOM 10 FOOD ITEMS ===")
    print(bottom_items_by_category(item_df, "Food"))

    # Demonstrate SQL query capability
    print("\n=== SQL QUERY: Top 5 Food Items by Revenue ===")
    sql = """
        SELECT [Item Name], SUM([Net Sales]) as Total_Revenue
        FROM sales
        WHERE [Sales Category] = 'Food'
        GROUP BY [Item Name]
        ORDER BY Total_Revenue DESC
        LIMIT 5
    """
    print(query_database(sql, db_path="Projects\\ToastMetrics\\toastmetrics.db"))
