import pandas as pd

# Load datasets
census_asrh_df = pd.read_csv('asrh/US_County_Level_Census_ASRH.csv')
census_total_df = pd.read_csv('totals/US_County_Level_Census_Totals.csv')

# Merge datasets on common columns
census_all_combined_df = pd.merge(
    census_asrh_df, census_total_df, on=['year', 'STNAME', 'CTYNAME'], how='inner'
)

# Rename columns for clarity
census_all_combined_df.rename(columns={'STNAME': 'state_name', 'CTYNAME': 'county_name'}, inplace=True)

# Check for null values and display a message
null_counts = census_all_combined_df.isnull().sum()
if null_counts.any():
    print("There are null values in the following columns:")
    print(null_counts[null_counts > 0])
else:
    print("There are no null values in any columns.")

# Save the combined dataframe to a CSV file
census_all_combined_df.to_csv('US_County_Level_Census.csv', index=False)
