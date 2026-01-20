import pandas as pd
import os
import glob
import warnings

warnings.filterwarnings('ignore')

source_dir = r"d:/all data science project/Sales dataset/sales dataset"
output_dir = r"d:/all data science project/Sales dataset/cleaned_data"
os.makedirs(output_dir, exist_ok=True)

files = glob.glob(os.path.join(source_dir, "*.csv"))

report = []

def clean_sales_data(df, filename):
    # Standardize column names
    df.columns = [c.strip() for c in df.columns]
    
    # Date parsing
    date_cols = [c for c in df.columns if 'date' in c.lower()]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Numeric conversion
    # Amount, Qty, Rate, Gross Amt
    numeric_cols = ['Amount', 'Qty', 'PCS', 'RATE', 'GROSS AMT', 'mrp', 'amount']
    for col in df.columns:
        if any(n in col.lower() for n in numeric_cols):
             df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop fully empty entries
    df.dropna(how='all', inplace=True)
    
    # Drop duplicates
    initial_rows = len(df)
    df.drop_duplicates(inplace=True)
    deduped_rows = len(df)
    
    duplicates_removed = initial_rows - deduped_rows
    
    # Fill critical missing values
    # For Amount/Qty, fill 0? Or drop? Let's fill 0 for now for reporting, but be careful.
    # Actually for Sales, if Order ID is present but Amount is NaN, maybe it's cancelled?
    # Let's just handle simple NaNs for categorical
    cat_cols = df.select_dtypes(include=['object']).columns
    df[cat_cols] = df[cat_cols].fillna('Unknown')
    
    return df, duplicates_removed

for file_path in files:
    filename = os.path.basename(file_path)
    try:
        # Try reading with default, if fail, try encoding
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except:
            df = pd.read_csv(file_path, encoding='ISO-8859-1')
            
        # Basic Strategy: 
        # If it has "Date" or "Order ID" or "SKU", treat as Sales.
        # If "Particular" or "Expense", treat as Financial.
        
        cols_lower = [c.lower() for c in df.columns]
        
        is_sales = any(x in cols_lower for x in ['date', 'order id', 'sku', 'asin'])
        
        cleaned_df, dups = clean_sales_data(df, filename)
        
        output_path = os.path.join(output_dir, f"cleaned_{filename}")
        cleaned_df.to_csv(output_path, index=False)
        
        report.append(f"{filename}: Success. Rows: {len(cleaned_df)}, Duplicates Removed: {dups}")
        
    except Exception as e:
        report.append(f"{filename}: Failed. Error: {str(e)}")

print("\n".join(report))
