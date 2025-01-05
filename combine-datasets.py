import pandas as pd

# Load datasets
election_results_df = pd.read_csv('election-results/US_County_Level_Presidential_Results.csv')
unemployment_rates_df = pd.read_csv('unemployment-rates/US_County_Level_Unemployment_Rates.csv')
county_level_census_data = pd.read_csv('census-data/US_County_Level_Census.csv')
county_level_satellite_images_df = pd.read_csv('satellite-images/US_County_Level_Satellite_Images.csv')
voter_turnout_df = pd.read_csv('voter-turnout/US_County_Level_Voter_Turnout.csv')
polls_df = pd.read_csv('polls/US_County_Level_Adjusted_Polls.csv')
betting_odds_df = pd.read_csv('betting-odds/US_Betting_Odds.csv')

# Rename columns for consistency
election_results_df.rename(columns={'county_fips': 'fips'}, inplace=True)

# Merge election results with unemployment rates
election_results_unemployment_df = pd.merge(
    election_results_df,
    unemployment_rates_df,
    on=['year', 'fips', 'county_name', 'state_name'],
    how='inner'
).drop_duplicates()

# Rename 'value' column to 'unemployment_rate'
election_results_unemployment_df.rename(columns={'value': 'unemployment_rate'}, inplace=True)

# Function to check for null values
def check_nulls(df):
    null_counts = df.isnull().sum()
    if null_counts.any():
        print("Null values found in the following columns:")
        print(null_counts[null_counts > 0])
    else:
        print("No null values detected.")

# Check for nulls in the merged unemployment data
check_nulls(election_results_unemployment_df)

# Merge with census data
census_combined_df = pd.merge(
    election_results_unemployment_df,
    county_level_census_data.drop_duplicates(),
    on=['year', 'county_name', 'state_name'],
    how='inner'
)

# Check for nulls in the final merged dataset
check_nulls(census_combined_df)

# Save the final dataset
census_combined_df.to_csv('combined-datasets/US_County_Level_Election_Results_Unemployment_Rates_Census.csv', index=False)

# Read the merged dataset again to check for any discrepancies
census_combined_df = pd.read_csv('combined-datasets/US_County_Level_Election_Results_Unemployment_Rates_Census.csv')

# Merge with satellite image data
satellite_combined_df = pd.merge(
    census_combined_df,
    county_level_satellite_images_df,
    on=['year', 'fips'],
    how='inner'
).drop_duplicates()

# Check for nulls in the merged satellite dataset
check_nulls(satellite_combined_df)

# Save the final dataset with satellite images
satellite_combined_df.to_csv(
    'combined-datasets/US_County_Level_Election_Results_Unemployment_Rates_Census_Satellite_Images.csv',
    index=False
)

# Read the merged dataset again to check for any discrepancies
satellite_combined_df = pd.read_csv('combined-datasets/US_County_Level_Election_Results_Unemployment_Rates_Census_Satellite_Images.csv')

# Merge with voter turnout data
voter_turnout_combined_df = pd.merge(satellite_combined_df, voter_turnout_df, on=['year', 'state_name', 'county_name'], how='inner')

# Drop duplicates from voter_turnout
voter_turnout_combined_df = voter_turnout_combined_df.drop_duplicates(subset=None, keep='first', inplace=False)

# Check for nulls in merged voter turnout data
check_nulls(voter_turnout_combined_df)

# Save the final dataset with voter turnout
voter_turnout_combined_df.to_csv(
    'combined-datasets/US_County_Level_Election_Results_Unemployment_Rates_Census_Satellite_Images_All_Voter_Turnout.csv',
    index=False
)

# Read the merged dataset again to check for any discrepancies
voter_turnout_combined_df = pd.read_csv('combined-datasets/US_County_Level_Election_Results_Unemployment_Rates_Census_Satellite_Images_All_Voter_Turnout.csv')

# Select columns from polls data
polls_df = polls_df[['year', 'county_fips', 'gop_pct_avg', 'dem_pct_avg', 'adjusted_gop_pct_estimate', 'adjusted_dem_pct_estimate']]

# Renameing county_fips column to fips
polls_df.rename(columns={'county_fips':'fips'}, inplace=True)

# Merge with polls data
polls_combined_df = pd.merge(voter_turnout_combined_df, polls_df, on=['year', 'fips'], how='inner')

# Check for nulls in merged polls data
check_nulls(polls_combined_df)

# Save the final dataset with polls
polls_combined_df.to_csv(
    'combined-datasets/US_County_Level_All_Adjusted_Polls.csv',
    index=False
)

# Read the merged dataset again to check for any discrepancies
polls_combined_df = pd.read_csv('combined-datasets/US_County_Level_All_Adjusted_Polls.csv')

# Merge with betting odds data
betting_odds_combined_df = pd.merge(polls_combined_df, betting_odds_df, on='year', how='left')

# Group by 'year' and compute the average of 'value'
avg_per_year = betting_odds_combined_df.groupby('year')[['gop_pct_avg', 'dem_pct_avg']].mean().reset_index()

# Merge the average back into the original dataframe with a custom column name
betting_odds_combined_df = betting_odds_combined_df.merge(avg_per_year, on='year', suffixes=('', '_per_year'))

# Getting per-county adjusted betting-odds percentage
betting_odds_combined_df = betting_odds_combined_df.assign(
adjusted_gop_pct_bo_avg=(
        betting_odds_combined_df['gop_pct_bo_avg'] * ((betting_odds_combined_df['gop_pct_avg'])/(betting_odds_combined_df['gop_pct_avg_per_year']))
    ).round(3)
)

betting_odds_combined_df = betting_odds_combined_df.assign(
    adjusted_dem_pct_bo_avg=(
        betting_odds_combined_df['dem_pct_bo_avg'] * ((betting_odds_combined_df['dem_pct_avg'])/(betting_odds_combined_df['dem_pct_avg_per_year']))
    ).round(3)
)

# Clipping betting-odds percentage to 100
betting_odds_combined_df['adjusted_dem_pct_bo_avg'] = betting_odds_combined_df['adjusted_dem_pct_bo_avg'].clip(upper=100)

# The minimum and maximum values for adjusted_gop_pct_bo_avg
min_value = betting_odds_combined_df['adjusted_gop_pct_bo_avg'].min()
max_value = betting_odds_combined_df['adjusted_gop_pct_bo_avg'].max()

# Printing maxium and minimum values
print(f"Min value adjusted_gop_pct_bo_avg: {min_value}")
print(f"Max value adjusted_gop_pct_bo_avg: {max_value}")

# The minimum and maximum values for adjusted_dem_pct_bo_avg
min_value = betting_odds_combined_df['adjusted_dem_pct_bo_avg'].min()
max_value = betting_odds_combined_df['adjusted_dem_pct_bo_avg'].max()

# Printing maxium and minimum values
print(f"Min value adjusted_dem_pct_bo_avg: {min_value}")
print(f"Max value adjusted_dem_pct_bo_avg: {max_value}")

# Dropping columns
betting_odds_combined_df = betting_odds_combined_df.drop(columns=['dem_pct_bo_avg', 'gop_pct_bo_avg',
       'gop_pct_avg_per_year', 'dem_pct_avg_per_year'])

# Removing duplicates
betting_odds_combined_df = betting_odds_combined_df.drop_duplicates(subset=None, keep='first', inplace=False)

# Check for nulls in merged betting odds data
check_nulls(betting_odds_combined_df)

# Adding party_won column to the betting_odds data
betting_odds_combined_df['party_won'] = betting_odds_combined_df.apply(lambda row: 'gop' if row['votes_gop'] > row['votes_dem'] else 'dem', axis=1)

# Save the final dataset with betting_odds
betting_odds_combined_df.to_csv(
    'combined-datasets/US_County_Level_All_Data.csv',
    index=False
)
