"""
Create test data files for comprehensive testing of all 4 features.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

os.makedirs('test_data', exist_ok=True)
print("Creating test data files...")

# Test 1: test_numeric.csv
print("Creating test_numeric.csv...")
np.random.seed(42)

df_numeric = pd.DataFrame({
    'skewed_values': np.random.exponential(scale=2, size=100),
    'zeros_column': np.random.choice([0, 1, 2, 3, 4, 5], size=100, p=[0.15, 0.17, 0.17, 0.17, 0.17, 0.17]),
    'amount': np.concatenate([np.random.uniform(100, 1000, size=95), [-50, -100, -25, -75, -200]]),
    'normal_numeric': np.random.normal(loc=50, scale=15, size=100)
})

df_numeric.to_csv('test_data/test_numeric.csv', index=False)
print("✓ test_numeric.csv created")

# Test 2: test_strings.csv
print("Creating test_strings.csv...")

with_spaces = []
for i in range(100):
    if i < 20:
        with_spaces.append(f" value_{i} ")
    else:
        with_spaces.append(f"value_{i}")

placeholders = ['N/A']*15 + ['null']*15 + ['unknown']*15 + ['TBD']*10 + ['valid_data']*35 + ['n/a']*10

casing_mix = ['Active']*33 + ['active']*33 + ['ACTIVE']*34

special_chars = ['value\twith\ttabs']*5 + [f'normal_value_{i}' for i in range(95)]

df_strings = pd.DataFrame({
    'with_spaces': with_spaces,
    'with_placeholders': placeholders[:100],
    'casing_mix': casing_mix,
    'with_special_chars': special_chars
})

df_strings.to_csv('test_data/test_strings.csv', index=False)
print("✓ test_strings.csv created")

# Test 3: test_dates.csv
print("Creating test_dates.csv...")

base_date = datetime(2020, 1, 1)
future_base = datetime(2026, 1, 1)

historical_dates = [base_date + timedelta(days=int(x)) for x in np.random.uniform(0, 1460, size=95)]
future_dates = [future_base + timedelta(days=int(x)) for x in np.random.uniform(0, 365, size=5)]
all_dates = historical_dates + future_dates
np.random.shuffle(all_dates)

df_dates = pd.DataFrame({
    'transaction_date': all_dates,
    'historical_only': [base_date + timedelta(days=int(x)) for x in np.random.uniform(0, 1460, size=100)]
})

df_dates.to_csv('test_data/test_dates.csv', index=False)
print("✓ test_dates.csv created")

# Test 4: test_duplicates.csv
print("Creating test_duplicates.csv...")

unique_rows = []
for i in range(120):
    unique_rows.append({
        'id': i,
        'name': f'customer_{i}',
        'value': np.random.randint(100, 1000),
        'status': np.random.choice(['active', 'inactive', 'pending'])
    })

duplicates = []
for _ in range(30):
    duplicates.append({'id': 200, 'name': 'duplicate_customer_1', 'value': 500, 'status': 'active'})
for _ in range(25):
    duplicates.append({'id': 201, 'name': 'duplicate_customer_2', 'value': 750, 'status': 'inactive'})
for _ in range(25):
    duplicates.append({'id': 202, 'name': 'duplicate_customer_3', 'value': 600, 'status': 'pending'})

all_rows = unique_rows + duplicates
df_duplicates = pd.DataFrame(all_rows)
df_duplicates = df_duplicates.sample(frac=1, random_state=42).reset_index(drop=True)

df_duplicates.to_csv('test_data/test_duplicates.csv', index=False)
print(f"✓ test_duplicates.csv created ({len(df_duplicates)} rows, {len(df_duplicates.drop_duplicates())} unique)")

# Test 5: test_all_features.csv
print("Creating test_all_features.csv...")
np.random.seed(42)
n_rows = 1000

skew_data = np.random.exponential(scale=3, size=n_rows)
zeros_data = np.where(np.random.random(n_rows) < 0.12, 0, np.random.uniform(1, 100, n_rows))
amount_data = np.where(np.random.random(n_rows) < 0.03, -np.random.uniform(10, 500, n_rows), np.random.uniform(50, 5000, n_rows))

string_data = []
for i in range(n_rows):
    if np.random.random() < 0.08:
        string_data.append(np.random.choice(['N/A', 'null', 'unknown', 'TBD']))
    else:
        string_data.append(f'customer_{i % 500}')

whitespace_data = [f'  value_{i}  ' if np.random.random() < 0.05 else f'value_{i}' for i in range(n_rows)]

casing_data = []
for i in range(n_rows):
    rand = np.random.random()
    if rand < 0.33:
        casing_data.append('Active')
    elif rand < 0.66:
        casing_data.append('active')
    else:
        casing_data.append('ACTIVE')

date_data = []
for i in range(n_rows):
    if np.random.random() < 0.02:
        date_data.append(future_base + timedelta(days=np.random.randint(0, 365)))
    else:
        date_data.append(base_date + timedelta(days=np.random.randint(0, 2000)))

df_all = pd.DataFrame({
    'skewed_numeric': skew_data,
    'zeros_numeric': zeros_data,
    'amount': amount_data,
    'description': string_data,
    'notes': whitespace_data,
    'status': casing_data,
    'transaction_date': date_data
})

for dup_set in range(5):
    dup_row = pd.DataFrame([{
        'skewed_numeric': 1.5,
        'zeros_numeric': 100.0,
        'amount': 1000.0,
        'description': f'duplicate_desc_{dup_set}',
        'notes': f'duplicate_notes_{dup_set}',
        'status': 'Active',
        'transaction_date': datetime(2023, 1, 1)
    }] * 10)
    df_all = pd.concat([df_all, dup_row], ignore_index=True)

df_all = df_all.sample(frac=1, random_state=42).reset_index(drop=True)
df_all.to_csv('test_data/test_all_features.csv', index=False)
print(f"✓ test_all_features.csv created ({len(df_all)} rows)")

print("\n" + "="*60)
print("Test data creation complete!")
print("="*60)
print("\nFiles created in test_data/:")
print("  ✓ test_numeric.csv (100 rows)")
print("  ✓ test_strings.csv (100 rows)")
print("  ✓ test_dates.csv (100 rows)")
print("  ✓ test_duplicates.csv (200 rows, 80 duplicates)")
print("  ✓ test_all_features.csv (1050 rows with all features)")
