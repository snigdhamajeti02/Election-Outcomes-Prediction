import pandas as pd
import numpy as np

# Load and filter the dataset for years >= 2008 and only for Republican and Democrat parties
df = pd.read_csv('original-data/countypres_2000-2020.csv')
df = df[(df['year'] >= 2008) & (df['party'].isin(['REPUBLICAN', 'DEMOCRAT']))].reset_index(drop=True)

# Calculate the percentage of votes for each candidate
df['percentage'] = df['candidatevotes'] / df['totalvotes'] * 100

# Group by relevant columns and sum the votes, then recalculate percentages
df_grouped = df.groupby(['year', 'state', 'county_name', 'county_fips', 'party'], as_index=False)[['candidatevotes', 'totalvotes']].sum()
df_grouped['percentage'] = df_grouped['candidatevotes'] / df_grouped['totalvotes'] * 100

# Pivot the data and rename columns for party percentages
df_pivot = df_grouped.pivot(index=['year', 'state', 'county_name', 'county_fips'], columns='party', values='percentage').reset_index()
df_pivot.columns.name = None
df_pivot = df_pivot.rename(columns={'DEMOCRAT': 'percentage_democrat', 'REPUBLICAN': 'percentage_republican'})

# Fill missing values in percentages with the average within each year group
df_pivot['percentage_democrat'] = df_pivot.groupby('year')['percentage_democrat'].transform(lambda x: x.fillna(x.mean()))
df_pivot['percentage_republican'] = df_pivot.groupby('year')['percentage_republican'].transform(lambda x: x.fillna(x.mean()))

# Convert county_fips to int64 and sort the DataFrame
df_pivot['county_fips'] = df_pivot['county_fips'].astype('int64')
df_pivot.sort_values(by=['year', 'county_fips', 'state', 'county_name'], inplace=True)

# Create lagged columns for previous years' percentages
for party in ['democrat', 'republican']:
    for lag in range(1, 3):
        df_pivot[f'previous_percentage_{party}_{lag}'] = df_pivot.groupby('county_fips')[f'percentage_{party}'].shift(lag)

# Calculate the average of previous two years for both parties
def calculate_average(prev_col1, prev_col2):
    return np.where(prev_col1.notna() & prev_col2.notna(), (prev_col1 + prev_col2) / 2, np.nan)

df_pivot['average_percentage_democrat'] = calculate_average(df_pivot['previous_percentage_democrat_1'], df_pivot['previous_percentage_democrat_2'])
df_pivot['average_percentage_republican'] = calculate_average(df_pivot['previous_percentage_republican_1'], df_pivot['previous_percentage_republican_2'])

# Filter for years > 2012 and apply mean fill for average percentages
df_pivot = df_pivot[df_pivot['year'] > 2012]
df_pivot[['average_percentage_democrat', 'average_percentage_republican']] = df_pivot[['average_percentage_democrat', 'average_percentage_republican']].apply(lambda x: x.fillna(df_pivot.groupby('year')[x.name].transform('mean')))

# Keep only relevant columns and capitalize the state names
df_pivot = df_pivot[['year', 'state', 'county_fips', 'percentage_democrat', 'percentage_republican',
                     'average_percentage_democrat', 'average_percentage_republican']]
df_pivot['state'] = df_pivot['state'].apply(lambda x: x.capitalize())

# Generate data for 2024 with NaN percentages, calculate averages, and append to the DataFrame
df_2024 = df_pivot[df_pivot['year'] == 2020].copy()
df_2024['year'] = 2024
df_2024[['percentage_democrat', 'percentage_republican']] = np.nan
df_2024['average_percentage_democrat'] = df_pivot.groupby('county_fips')['percentage_democrat'].transform('mean')
df_2024['average_percentage_republican'] = df_pivot.groupby('county_fips')['percentage_republican'].transform('mean')

df_final = pd.concat([df_pivot, df_2024], ignore_index=True)

# Filter for counties with county_fips < 58000
df_final = df_final[['year', 'state', 'county_fips', 'average_percentage_democrat', 'average_percentage_republican']]
df_final = df_final[df_final['county_fips'] < 58000]

# Check for null values and display a message
if df_final.isnull().sum().any():
    print("There are null values in the following columns:")
    print(df_final.isnull().sum()[df_final.isnull().sum() > 0])
else:
    print("There are no null values in any columns.")

# Reset the index after all modifications and save to CSV
df_final.reset_index(drop=True, inplace=True)
df_final.to_csv('US_County_Level_Historical_Election_Results.csv', index=False)
