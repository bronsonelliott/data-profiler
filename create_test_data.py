import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Create a realistic BI-style dataset
np.random.seed(42)
n_rows = 500

# Generate realistic data
customer_ids = [f'CUST{i:05d}' for i in range(n_rows)]
order_ids = [f'ORD{i:06d}' for i in range(n_rows)]
regions = np.random.choice(['North', 'South', 'East', 'West'], n_rows)
categories = np.random.choice(['Electronics', 'Clothing', 'Food', 'Books', 'Home'], n_rows)
statuses = np.random.choice(['Active', 'Pending', 'Cancelled', 'Completed'], n_rows, p=[0.5, 0.2, 0.1, 0.2])
revenues = np.random.uniform(10, 5000, n_rows).round(2)
quantities = np.random.randint(1, 50, n_rows)
discounts = np.random.uniform(0, 30, n_rows).round(1)
dates = [(datetime(2024, 1, 1) + timedelta(days=int(x))).strftime('%Y-%m-%d') for x in np.random.uniform(0, 365, n_rows)]

# Column with missing values (25%)
emails = [f'customer{i}@example.com' if i % 4 != 0 else None for i in range(n_rows)]

# Dominant value column (96% one value)
notes = []
for i in range(n_rows):
    if i < int(n_rows * 0.96):
        notes.append('Standard order')
    else:
        notes.append(np.random.choice(['Rush', 'Gift', 'Special']))

# Constant column
warehouse = ['W1'] * n_rows

data = {
    'customer_id': customer_ids,
    'order_id': order_ids,
    'region': regions,
    'product_category': categories,
    'status': statuses,
    'revenue': revenues,
    'quantity': quantities,
    'discount_pct': discounts,
    'order_date': dates,
    'customer_email': emails,
    'notes': notes,
    'warehouse_code': warehouse,
}

df = pd.DataFrame(data)
df.to_csv('test_data/bi_dataset.csv', index=False)
print(f'Created test_data/bi_dataset.csv with shape {df.shape}')
