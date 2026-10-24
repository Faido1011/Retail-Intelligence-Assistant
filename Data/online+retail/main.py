
from pathlib import Path
import pandas as pd

file_path = Path(__file__).parent / "Online Retail.xlsx"
df = pd.read_excel(file_path)

print("=== ORIGINAL DATASET ===")
print("Rows:", len(df))
print("Columns:", len(df.columns))

df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
df["Description"] = df["Description"].fillna("Unknown product")

# Create a preliminary sales dataset
sales_df = df[
    (df["Quantity"] > 0) &
    (df["UnitPrice"] >= 0)
].copy()

sales_df["Revenue"] = sales_df["Quantity"] * sales_df["UnitPrice"]

print("\n=== CLEANING RESULTS ===")
print("Original rows:", len(df))
print("Rows in preliminary sales view:", len(sales_df))
print("Rows excluded:", len(df) - len(sales_df))
print("Missing CustomerIDs:", sales_df["CustomerID"].isna().sum())

print("\n=== SALES SUMMARY ===")
print("Total line revenue (£):", round(sales_df["Revenue"].sum(), 2))
print("Unique invoices:", sales_df["InvoiceNo"].nunique())
print("Unique products:", sales_df["StockCode"].nunique())
print("Countries:", sales_df["Country"].nunique())

top_products = (
    sales_df.groupby("Description")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print("\n=== TOP 10 PRODUCTS BY REVENUE ===")
print(top_products)

top_countries = (
    sales_df.groupby("Country")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print("\n=== TOP 10 COUNTRIES BY REVENUE ===")
print(top_countries)

output_path = Path(__file__).parent / "cleaned_sales.csv"
sales_df.to_csv(output_path, index=False)

print("\nCleaned sales data saved to:", output_path)
