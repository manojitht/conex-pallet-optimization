import pandas as pd
import numpy as np
import random

df = pd.read_csv('real_data/shipoci_dataset.csv')

# Expand rows so every individual pallet has its own row
df_expanded = df.loc[df.index.repeat(df['pallets'])].reset_index(drop=True)

df_expanded['per_pallet_weight'] = df_expanded['weight'] / df_expanded['pallets']
df_expanded['per_pallet_cube'] = df_expanded['cube'] / df_expanded['pallets']

synthetic_df = pd.DataFrame()

# Generate sequential IDs (P1, P2, P3...)
synthetic_df['id'] = ['P' + str(i+1) for i in range(len(df_expanded))]

synthetic_df['origin'] = np.random.choice(['EU', 'NA'], size=len(df_expanded))

conditions = [
    (df_expanded['per_pallet_cube'] > 30),
    (df_expanded['per_pallet_cube'] <= 30)
]
choices_size = ['FULL', 'HALF']
choices_length = [4, 2]
choices_width = [3, 3]

synthetic_df['pallet_size'] = np.select(conditions, choices_size, default='FULL')
synthetic_df['length'] = np.select(conditions, choices_length, default=4)
synthetic_df['width'] = np.select(conditions, choices_width, default=3)

# Calculate Height based on Volume formula: H = V / (L * W)
synthetic_df['height'] = np.round(df_expanded['per_pallet_cube'] / (synthetic_df['length'] * synthetic_df['width'])).astype(int)
# Ensure height is at least 1
synthetic_df['height'] = synthetic_df['height'].clip(lower=1) 

# Map Weight (rounded to integer as seen in target)
synthetic_df['weight'] = np.round(df_expanded['per_pallet_weight']).astype(int)

# Randomly assign distances 
synthetic_df['distance'] = np.random.choice([100, 300, 900], size=len(df_expanded))

# Map Descriptions to Synthetic 'Goods' Categories
def map_goods(desc):
    desc = str(desc).upper()
    if 'REFRIGERATED' in desc or 'FROZEN' in desc or 'GROCERY' in desc:
        return random.choice(['Food', 'Pharmaceuticals'])
    elif 'DRY' in desc or 'GENERAL' in desc:
        return random.choice(['Furniture', 'Electronics', 'Chemicals'])
    return 'Other'

synthetic_df['goods'] = df_expanded['description'].apply(map_goods)

# Boolean flags based on goods type
synthetic_df['fragile'] = synthetic_df['goods'].isin(['Electronics', 'Pharmaceuticals'])
synthetic_df['stackable'] = ~synthetic_df['fragile'] # Assuming fragile items aren't stackable

# Assign max stack weight (0 if not stackable, else random reasonable limit)
synthetic_df['max_stack_weight'] = np.where(synthetic_df['stackable'], np.random.randint(300, 1000, size=len(df_expanded)), 0)

# Generate synthetic financial metrics based on weight and distance
synthetic_df['cost'] = np.round((synthetic_df['weight'] * 0.5) + (synthetic_df['distance'] * 0.2)).astype(int)
synthetic_df['profit'] = np.round(synthetic_df['cost'] * np.random.uniform(1.5, 3.0, size=len(df_expanded))).astype(int)

print(synthetic_df.head())
synthetic_df.to_csv('real_data/shipoci_dataset_transformed.csv', index=False)

