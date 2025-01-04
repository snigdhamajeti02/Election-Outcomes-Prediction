import os
import pandas as pd

# Load datasets
combined_data = pd.read_csv('../combined-datasets/US_County_Level_Election_Results_Unemployment_Rates_Census_Satellite_Images.csv')
voter_turnout_df = pd.read_csv('US_State_Level_Voter_Turnout.csv')

# Identify the population columns
pop_columns = [col for col in combined_data.columns if 'POP' in col and 'TOT' in col and col.split('_')[-1] not in ['0', '1', '2', '3', '4']]

# Prepare census data with population columns and eligible voters calculation
census_data = combined_data[['year', 'state_name', 'county_name', 'total_votes'] + pop_columns]

census_data = census_data.copy()
census_data['ELIGIBLE_VOTERS'] = census_data[pop_columns].sum(axis=1)

# Merge census data with voter turnout data
merged_df = census_data.merge(voter_turnout_df, on=['year', 'state_name'], how='left')

# Fill missing turnout values for specific years using US national percentages from dataset
turnout_fills = {2016: 60.1, 2020: 66.6, 2024: 63.7}
for year, turnout in turnout_fills.items():
    merged_df.loc[merged_df['year'] == year, 'Turnout Percentage'] = merged_df.loc[merged_df['year'] == year, 'Turnout Percentage'].fillna(turnout)

# Rename 'Turnout Percentage' to 'voter_turnout_pct'
merged_df.rename(columns={'Turnout Percentage': 'voter_turnout_pct'}, inplace=True)

# Add total eligible voters and total votes by state
merged_df['TOT_ELIGIBLE_VOTERS'] = merged_df.groupby('state_name')['ELIGIBLE_VOTERS'].transform('sum')
merged_df['total_state_votes'] = merged_df.groupby('state_name')['total_votes'].transform('sum')

# Calculate adjusted voter turnout percentages based on population and votes
merged_df['adjusted_voter_turnout_pct_pop'] = (
    merged_df['voter_turnout_pct'] * (1 + merged_df['ELIGIBLE_VOTERS'] / merged_df['TOT_ELIGIBLE_VOTERS'])
).round(3)

merged_df['adjusted_voter_turnout_pct_votes'] = (
    merged_df['voter_turnout_pct'] * (1 + merged_df['total_votes'] / merged_df['total_state_votes'])
).round(3)

# Clip adjusted voter turnout percentages to 100
merged_df['adjusted_voter_turnout_pct_pop'] = merged_df['adjusted_voter_turnout_pct_pop'].clip(upper=100)
merged_df['adjusted_voter_turnout_pct_votes'] = merged_df['adjusted_voter_turnout_pct_votes'].clip(upper=100)

# Calculate adjusted voter turnout based on the percentages
merged_df['adjusted_voter_turnout'] = merged_df['adjusted_voter_turnout_pct_pop'] / 100
merged_df['adjusted_voter_turnout_votes'] = merged_df['adjusted_voter_turnout_pct_votes'] / 100

# Rearrange columns to a consistent order
merged_df = merged_df[['year', 'state_name', 'county_name', 'adjusted_voter_turnout', 'adjusted_voter_turnout_votes']]

# Check for null values in the merged DataFrame
null_counts = merged_df.isnull().sum()
if null_counts.any():
    print("Null values found in the following columns:")
    print(null_counts[null_counts > 0])
else:
    print("No null values detected.")

# Save the combined DataFrame to a CSV
merged_df.to_csv('US_County_Level_Voter_Turnout.csv', index=False)
