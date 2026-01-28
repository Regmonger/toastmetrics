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

# Me: Copilot, ChatGPT gave me the code for this application. Do you see any issues with it?
# Copilot: The code looks well-structured and accomplishes the task of loading and analyzing menu-breakdown CSV files effectively.
# However, there are a few potential improvements and considerations:
# 1. Error Handling: The code currently does not include error handling for file reading operations. 
# It would be beneficial to add try-except blocks around file I/O operations to handle cases where files may not be accessible or are corrupted.
# 2. Performance: If the dataset is large, consider optimizing the data loading and processing steps.
# For example, using chunksize in pandas.read_csv() can help manage memory usage.
# 3. Logging: Instead of using print statements, consider using the logging module for better control over logging levels and outputs.
# 4. Documentation: While the functions have docstrings, adding more detailed explanations and examples could enhance usability for other developers.
# 5. Type Annotations: The code could benefit from more consistent use of type annotations for function parameters and return types to improve code clarity and facilitate static analysis.
# 6. Unit Tests: Implementing unit tests for the functions would help ensure the code's reliability and make future modifications safer.
# Overall, the code is functional and clear, but addressing these points could enhance its robustness and maintainability.
# Me: Thank you. This is intended to be the 2nd of two portfolio projects demonstrating my Python skills. The first project is the file that is
# currently open titled waste_tracker.py. I just want to make sure that project 2 is as good as it can be.
# Copilot: Understood. The ToastMetrics application you've provided is a solid demonstration of your Python skills,  
# particularly in data manipulation and analysis using pandas. Here are some additional suggestions to further enhance the quality of your project:
# 1. Modularization: Consider breaking down the code into smaller modules or classes if the project expands in the future.
#    This can help in organizing the code better and making it more maintainable.
# 2. User Interface: If this application is intended for end-users, consider adding a simple command-line interface (CLI) 
#    or graphical user interface (GUI) to allow users to specify the base path and other parameters interactively.
# 3. Configuration: Use a configuration file (e.g., JSON, YAML) to manage settings like the base path, output options, and analysis parameters.
# This can make the application more flexible and easier to configure without changing the code.