import os
import pandas as pd

def load_and_clean_data(file_path, year):
    # Load dataset
    df = pd.read_csv(file_path, encoding='ISO-8859-1')

    # Select columns related to the year
    year_columns = [col for col in df.columns if str(year) in col]
    columns_to_keep = ['STNAME', 'CTYNAME'] + year_columns
    df = df[columns_to_keep]

    # Clean column names
    df.columns = [col.replace(str(year), '').replace('_', '') for col in df.columns]

    # Add year column
    year = 2024 if year == 2023 else year
    df.insert(0, 'year', year)

    return df

# Load and clean data for 2016, 2020, and 2023
census_2016_df = load_and_clean_data('co-est2016-alldata.csv', year=2016)
census_2020_df = load_and_clean_data('co-est2020-alldata.csv', year=2020)
census_2023_df = load_and_clean_data('co-est2023-alldata.csv', year=2023)

# Rename specific columns for 2023 dataset
census_2023_df = census_2023_df.rename(columns={'NATURALCHG': 'NATURALINC', 'RNATURALCHG': 'RNATURALINC'})

# Combine datasets
census_totals_combined_df = pd.concat([census_2016_df, census_2020_df, census_2023_df], axis=0, ignore_index=True)

# Check for null values and print a message
null_counts = census_totals_combined_df.isnull().sum()
if null_counts.any():
    print("There are null values in the following columns:")
    print(null_counts[null_counts > 0])
else:
    print("There are no null values in any columns.")

# Save the combined dataframe to a CSV file
census_totals_combined_df.to_csv('US_County_Level_Census_Totals.csv', index=False)
