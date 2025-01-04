import pandas as pd

# Initialize the list to store data
text_data = []

# Read the data and process it
with open('voter-turnout-percentage.txt', 'r') as file:
    for line in file:
        if 'turnout' not in line:
            text_data.append([line.split('\t')[i] for i in range(6) if i not in [2, 4]])

# Create DataFrame from the processed data
voter_turnout_df = pd.DataFrame(text_data[1:], columns=text_data[0])

# Define a function to clean percentage columns
def clean_percentage_column(df, column):
    df[column] = df[column].replace('%', '', regex=True).apply(pd.to_numeric, errors='coerce')

# Clean the percentage columns for 2016, 2020, and 2024
for year in ['2016', '2020', '2024']:
    clean_percentage_column(voter_turnout_df, year)

# Fill missing values for 2016 by averaging 2024 and 2020 values
voter_turnout_df['2016'] = voter_turnout_df.apply(
    lambda row: round((row['2024'] + row['2020']) / 2, 1) if pd.isna(row['2016']) else row['2016'],
    axis=1
)

# Reshape the data to a long format
voter_turnout_df = pd.melt(voter_turnout_df, id_vars=['State'], var_name='Year', value_name='Turnout Percentage')

# Sort the DataFrame by 'Year' and 'State'
voter_turnout_df.sort_values(by=['Year', 'State'], ascending=[True, True], inplace=True)

# Rename columns for clarity
voter_turnout_df.rename(columns={'State': 'state_name', 'Year': 'year'}, inplace=True)

# Reset the index and select the final columns
voter_turnout_df = voter_turnout_df.reset_index(drop=True)
voter_turnout_df = voter_turnout_df[['year', 'state_name', 'Turnout Percentage']]

# Ensure 'year' is of integer type
voter_turnout_df['year'] = voter_turnout_df['year'].astype('int64')

# Check for null values and display a message
null_counts = voter_turnout_df.isnull().sum()
if null_counts.any():
    print("There are null values in the following columns:")
    print(null_counts[null_counts > 0])
else:
    print("There are no null values in any columns.")

# Save the cleaned DataFrame to a CSV file
voter_turnout_df.to_csv('US_State_Level_Voter_Turnout.csv', index=False)
