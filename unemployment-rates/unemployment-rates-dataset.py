import os
import pandas as pd

# Load the CSV data
csv_path = r'unemployment.csv'
unemployment_rates_df = pd.read_csv(csv_path, low_memory=False)

# Function to process DataFrame for a specific year
def process_year_data(df, year):
    # Filter by year and reset index
    df_year = df[df['year'] == year].reset_index(drop=True)

    # Convert 'value' column to numeric, coercing errors to NaN
    df_year['value'] = pd.to_numeric(df_year['value'], errors='coerce')

    # Group by relevant columns and calculate the mean of 'value'
    df_year = df_year.groupby(['year', 'fips', 'county_name', 'state_name'], as_index=False).agg({'value': 'mean'})

    # Sort by 'fips' and reset index
    df_year = df_year.sort_values(by=['fips']).reset_index(drop=True)
    return df_year

# Process data for specific years (2016, 2020, 2023)
unemployment_rates_2016_df = process_year_data(unemployment_rates_df, 2016)
unemployment_rates_2020_df = process_year_data(unemployment_rates_df, 2020)
unemployment_rates_2023_df = process_year_data(unemployment_rates_df, 2023)

# Copy 2023 data for 2024 and update the year
unemployment_rates_2024_df = unemployment_rates_2023_df.copy()
unemployment_rates_2024_df['year'] = 2024

# Combine the DataFrames
unemployment_rates_combined_df = pd.concat([unemployment_rates_2016_df, unemployment_rates_2020_df, unemployment_rates_2024_df], axis=0, ignore_index=True)

# Check for null values and print appropriate message
null_counts = unemployment_rates_combined_df.isnull().sum()
if null_counts.any():
    print("There are null values in the following columns:")
    print(null_counts[null_counts > 0])
else:
    print("There are no null values in any columns.")

# Ensure 'value' is of type float64
unemployment_rates_combined_df['value'] = unemployment_rates_combined_df['value'].astype('float64')

# Save the combined DataFrame to CSV
unemployment_rates_combined_df.to_csv('US_County_Level_Unemployment_Rates.csv', index=False)
