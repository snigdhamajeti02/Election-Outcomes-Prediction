import pandas as pd

# Load datasets
election_results_df = pd.read_csv('election-results/US_County_Level_Presidential_Results.csv')
unemployment_rates_df = pd.read_csv('unemployment-rates/US_County_Level_Unemployment_Rates.csv')
county_level_census_data = pd.read_csv('census-data/US_County_Level_Census.csv')
county_level_satellite_images_df = pd.read_csv('satellite-images/US_County_Level_Satellite_Images.csv')
voter_turnout_df = pd.read_csv('voter-turnout/US_County_Level_Voter_Turnout.csv')

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

voter_turnout_combined_df = pd.merge(satellite_combined_df, voter_turnout_df, on=['year', 'state_name', 'county_name'], how='inner')

voter_turnout_combined_df = voter_turnout_combined_df.drop_duplicates(subset=None, keep='first', inplace=False)

check_nulls(voter_turnout_combined_df)

# Save the final dataset with voter turnout
voter_turnout_combined_df.to_csv(
    'combined-datasets/US_County_Level_Election_Results_Unemployment_Rates_Census_Satellite_Images_All_Voter_Turnout.csv',
    index=False
)
