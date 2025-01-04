import os
import pandas as pd

# Function to load CSV files
def load_betting_odds(file_path):
    return pd.read_csv(file_path)

# Function to calculate weighted averages for 'dem_pct_bo' and 'gop_pct_bo' columns
def calculate_weighted_avg(df, col1, col2, year):
    # Assign weights in descending order
    df['weight'] = df.index[::-1] + 1  # This will give reverse weight based on index

    # Calculate weighted averages
    dem_avg = (df[col1] * df['weight']).sum() / df['weight'].sum()
    gop_avg = (df[col2] * df['weight']).sum() / df['weight'].sum()

    # Return a DataFrame with the year and the calculated averages
    return pd.DataFrame({
        'year': [year],
        'dem_pct_bo_avg': [dem_avg],
        'gop_pct_bo_avg': [gop_avg]
    })

# File paths for the datasets
file_paths = [
    ('betting-odds-2016.csv', 2016),
    ('betting-odds-2020.csv', 2020),
    ('betting-odds-2024.csv', 2024)
]

# List to store dataframes
dfs = []

# Process each file and calculate averages
for file_path, year in file_paths:
    df = load_betting_odds(file_path)
    avg_df = calculate_weighted_avg(df, 'dem_pct_bo', 'gop_pct_bo', year)
    dfs.append(avg_df)

# Concatenate all DataFrames and remove duplicates
combined_df = pd.concat(dfs, ignore_index=True).drop_duplicates().reset_index(drop=True)

# Check for null values and print appropriate message
null_counts = combined_df.isnull().sum()
if null_counts.any():
    print("There are null values in the following columns:")
    print(null_counts[null_counts > 0])
else:
    print("There are no null values in any columns.")

# Save the final DataFrame to CSV
combined_df.to_csv('US_Betting_Odds.csv', index=False)
