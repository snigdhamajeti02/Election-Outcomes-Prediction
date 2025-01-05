import pandas as pd

election_results_df = pd.read_csv('../historical-elections/US_County_Level_Historical_Election_Results.csv')
poll_results_df = pd.read_csv('US_State_Level_Polls.csv')

election_results_df.rename(columns={'state': 'state_name'}, inplace=True)

# Function to convert string to title case
def to_title_case(s):
    return s.title()

# Apply the function to the 'state_name' column
election_results_df['state_name'] = election_results_df['state_name'].apply(to_title_case)

# Merge on 'year' and 'state_name' to add state-level data to county-level rows
merged_df = pd.merge(election_results_df, poll_results_df, on=['year', 'state_name'], how='left')

# Function to impute NaN values with the mean for a specific year
def impute_by_year(df, column):
    # Group by 'year' and calculate the mean for the specified column
    mean_by_year = df.groupby('year')[column].transform('mean')

    # Impute NaN values with the mean for the specific year
    df[column] = df[column].fillna(mean_by_year)

    return df

# Impute 'gop_pct_estimate' and 'dem_pct_estimate' columns
df = impute_by_year(merged_df, 'gop_pct_estimate')
df = impute_by_year(merged_df, 'dem_pct_estimate')

merged_df = df.copy()

merged_df.rename(columns={'average_percentage_democrat':'dem_pct_avg', 'average_percentage_republican':'gop_pct_avg'}, inplace=True)

merged_df = merged_df.assign(
    adjusted_gop_pct_estimate=(
        merged_df['gop_pct_estimate'] * (1 + ((merged_df['gop_pct_avg'] - merged_df['gop_pct_estimate'])/(100)))
    ).round(3)
)

merged_df = merged_df.assign(
    adjusted_dem_pct_estimate=(
        merged_df['dem_pct_estimate'] * (1 + ((merged_df['dem_pct_avg'] - merged_df['dem_pct_estimate'])/(100)))
    ).round(3)
)

# Find the maximum value of the 'county_fips' column
max_value = merged_df['adjusted_gop_pct_estimate'].max()
print("Maximum value adjusted_gop_pct_estimate:", max_value)

# Find the minimum value of the 'county_fips' column
min_value = merged_df['adjusted_gop_pct_estimate'].min()
print("Minimum value adjusted_gop_pct_estimate:", min_value)

# Find the maximum value of the 'county_fips' column
max_value = merged_df['adjusted_dem_pct_estimate'].max()
print("Maximum value adjusted_dem_pct_estimate:", max_value)

# Find the minimum value of the 'county_fips' column
min_value = merged_df['adjusted_dem_pct_estimate'].min()
print("Minimum value adjusted_dem_pct_estimate:", min_value)

# Check for null values in the merged DataFrame
null_counts = merged_df.isnull().sum()
if null_counts.any():
    print("Null values found in the following columns:")
    print(null_counts[null_counts > 0])
else:
    print("No null values detected.")

merged_df.to_csv('US_County_Level_Adjusted_Polls.csv', index=False)
