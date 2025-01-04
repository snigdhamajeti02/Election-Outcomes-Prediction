import pandas as pd

# File paths for the poll data
poll_files = {
    2016: 'US_State_Level_2016_Polls.csv',
    2020: 'US_State_Level_2020_Polls.csv',
    2024: 'US_State_Level_2024_Polls.csv'
}

# Load and combine data
polls_combined_df = pd.concat(
    [pd.read_csv(file) for file in poll_files.values()],
    axis=0, ignore_index=True
)

# Rename columns for consistency
polls_combined_df.rename(columns={'cycle': 'year', 'state': 'state_name'}, inplace=True)

# Check for null values and print the appropriate message
null_counts = polls_combined_df.isnull().sum()
if null_counts.any():
    print("There are null values in the following columns:")
    print(null_counts[null_counts > 0])
else:
    print("There are no null values in any columns.")

# Save the combined DataFrame to a new CSV
polls_combined_df.to_csv('US_State_Level_Polls.csv', index=False)
