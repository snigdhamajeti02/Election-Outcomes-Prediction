import os
import pandas as pd
from tqdm import tqdm

def load_and_clean_data(file_path, year_filter):
    # Load dataset
    df = pd.read_csv(file_path, encoding='ISO-8859-1', low_memory=False)

    # Filter by the specified year
    df = df[df['YEAR'] == year_filter]
    df = df.reset_index(drop=True)

    return df

def pivot_columns(df, columns_to_pivot):
    # Create a copy of the DataFrame to avoid modifying the original
    df_copy = df.copy()

    for col in tqdm(columns_to_pivot, desc="pivoting columns"):
        # Pivot the column based on AGEGRP
        df_temp = df_copy.pivot_table(
            index=['SUMLEV', 'STATE', 'COUNTY', 'STNAME', 'CTYNAME', 'YEAR'],
            columns='AGEGRP', values=col, aggfunc='first'
        )

        # Rename columns to include AGEGRP index
        df_temp.columns = [f'{col}_{agegrp}' for agegrp in df_temp.columns]

        # Merge the pivoted DataFrame with the original DataFrame
        df_copy = df_copy.drop(col, axis=1).merge(df_temp,
                                                  on=['SUMLEV', 'STATE', 'COUNTY', 'STNAME', 'CTYNAME', 'YEAR'],
                                                  how='left')

    # Drop unnecessary columns and reset the index
    df_copy.drop(columns=['SUMLEV', 'STATE', 'COUNTY', 'YEAR', 'AGEGRP'], inplace=True)
    df_copy = df_copy.drop_duplicates(subset=None, keep='first', inplace=False).reset_index(drop=True)

    return df_copy

# Load and clean data for 2016, 2020, and 2023
census_2016 = load_and_clean_data('cc-est2016-alldata.csv', year_filter=9)
census_2020 = load_and_clean_data('cc-est2020-alldata.csv', year_filter=13)
census_2023 = load_and_clean_data('cc-est2023-alldata.csv', year_filter=5)

# Define columns to pivot based on pattern (MALE or POP)
columns_to_pivot = lambda df: [col for col in df.columns if 'MALE' in col or 'POP' in col]

# Pivot the datasets
census_2016_pivoted = pivot_columns(census_2016, columns_to_pivot(census_2016))
census_2020_pivoted = pivot_columns(census_2020, columns_to_pivot(census_2020))
census_2023_pivoted = pivot_columns(census_2023, columns_to_pivot(census_2023))

# Add year columns for each dataset
census_2016_pivoted.insert(0, 'year', 2016)
census_2020_pivoted.insert(0, 'year', 2020)
census_2023_pivoted.insert(0, 'year', 2024)

# Combine the dataframes
combined_df = pd.concat([census_2016_pivoted, census_2020_pivoted, census_2023_pivoted], axis=0, ignore_index=True)

# Check for null values
null_counts = combined_df.isnull().sum()
if null_counts.any():
    print("There are null values in the following columns:")
    print(null_counts[null_counts > 0])
else:
    print("There are no null values in any columns.")

# Save the combined dataframe to a CSV file
combined_df.to_csv('US_County_Level_Census_ASRH.csv', index=False)
