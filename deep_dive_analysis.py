import pandas as pd
import os

data_path = r"d:/all data science project/Sales dataset/cleaned_data/cleaned_Amazon-Sale-Report.csv"

try:
    df = pd.read_csv(data_path, low_memory=False)
    
    # Preprocessing
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Month'] = df['Date'].dt.to_period('M')
    
    # 1. Trend Analysis
    monthly_sales = df.groupby('Month')['Amount'].sum()
    print("--- Monthly Sales ---")
    print(monthly_sales)
    
    # Growth Calculation (Last Month vs First Month or Month-over-Month)
    if len(monthly_sales) > 1:
        first_month = monthly_sales.iloc[0]
        last_month = monthly_sales.iloc[-1]
        growth = ((last_month - first_month) / first_month) * 100
        print(f"\nOverall Growth: {growth:.2f}%")
        
        # Check decline in recent months
        recent_growth = monthly_sales.pct_change().tail(3)
        print("\nRecent Month-over-Month Growth:")
        print(recent_growth)
        
    # 2. Reasons (Cancellation Rate)
    # Check 'Status' column
    print("\n--- Status Distribution ---")
    status_counts = df['Status'].value_counts(normalize=True) * 100
    print(status_counts.head(5))
    
    cancellation_rate = status_counts.get('Cancelled', 0)
    print(f"\nCancellation Rate: {cancellation_rate:.2f}%")
    
    # 3. Fulfillment Impact
    print("\n--- Fulfillment Analysis ---")
    if 'Fulfilled-by' in df.columns:
        fulfillment_sales = df.groupby('Fulfilled-by')['Amount'].sum()
    elif 'fulfilled-by' in df.columns:
        fulfillment_sales = df.groupby('fulfilled-by')['Amount'].sum()
    else:
        fulfillment_sales = "Column not found"
    print(fulfillment_sales)

    # 4. Quantity vs Amount (Discounting?)
    # Avg Price per unit over time
    df['AvgPrice'] = df['Amount'] / df['Qty']
    monthly_avg_price = df.groupby('Month')['AvgPrice'].mean()
    print("\n--- Monthly Avg Price per Unit ---")
    print(monthly_avg_price)

except Exception as e:
    print(f"Error: {e}")
