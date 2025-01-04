import pandas as pd

# Load the datasets
poll_files = {
    2016: 'original-data/pres_pollaverages_1968-2016.csv',
    2020: 'original-data/presidential_poll_averages_2020.csv',
    2024: 'original-data/presidential_poll_averages_2024.csv'
}

# Read and filter datasets by cycle year
state_polls_df = {
    year: pd.read_csv(file).query('cycle == @year')
    for year, file in poll_files.items()
}

# Rename 'candidate' column for consistency across datasets
state_polls_df[2024].rename(columns={'candidate': 'candidate_name'}, inplace=True)

# Define candidate names for each year
candidate_names = {
    2016: ["Donald Trump", "Hillary Rodham Clinton"],
    2020: ["Donald Trump", "Joseph R. Biden Jr."],
    2024: ["Trump", "Harris"]
}

# Filter datasets based on candidate names
for year, names in candidate_names.items():
    state_polls_df[year] = state_polls_df[year][state_polls_df[year]['candidate_name'].isin(names)].reset_index(drop=True)

# Function to assign party based on candidate name
def assign_party(candidate_name):
    if candidate_name in ['Trump', 'Donald Trump']:
        return 'gop'
    elif candidate_name in ['Harris', 'Joseph R. Biden Jr.', 'Hillary Rodham Clinton']:
        return 'dem'

# Helper function to process and merge data for each election year
def process_year_data(df, year):
    # Group by 'cycle', 'state', and 'candidate_name' to calculate mean pct_estimate
    avg_pct = df.groupby(['cycle', 'state', 'candidate_name'])['pct_estimate'].mean().reset_index()
    avg_pct['party'] = avg_pct['candidate_name'].apply(assign_party)
    avg_pct = avg_pct[['cycle', 'state', 'party', 'pct_estimate']]

    # Separate data by party and rename pct_estimate columns
    df_gop = avg_pct[avg_pct['party'] == 'gop'][['cycle', 'state', 'pct_estimate']].rename(columns={'pct_estimate': 'gop_pct_estimate'})
    df_dem = avg_pct[avg_pct['party'] == 'dem'][['cycle', 'state', 'pct_estimate']].rename(columns={'pct_estimate': 'dem_pct_estimate'})

    # Merge gop and dem DataFrames on 'cycle' and 'state'
    result = pd.merge(df_gop, df_dem, on=['cycle', 'state'])

    return result

# Process data for each year and store results
results = {year: process_year_data(df, year) for year, df in state_polls_df.items()}

# Check for null values and display a message
for year, result in results.items():
    if result.isnull().sum().any():
        print(f"There are null values in the following columns for {year} year:")
        print(result.isnull().sum()[result.isnull().sum() > 0])
    else:
        print(f"There are no null values in any columns for {year}.")

# Save results to CSV
for year, result in results.items():
    result.to_csv(f'US_State_Level_{year}_Polls.csv', index=False)
