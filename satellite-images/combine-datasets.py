import os
import pandas as pd

# Read CSV files for each year
satelitte_images_2016_df = pd.read_csv('US_County_2016_Satellite_Images.csv')
satelitte_images_2020_df = pd.read_csv('US_County_2020_Satellite_Images.csv')
satelitte_images_2023_df = pd.read_csv('US_County_2023_Satellite_Images.csv')

# Insert 'year' column to each DataFrame
satelitte_images_2016_df.insert(0, 'year', 2016)
satelitte_images_2020_df.insert(0, 'year', 2020)
satelitte_images_2023_df.insert(0, 'year', 2024)

# Combine the DataFrames into one
satellite_images_combined_df = pd.concat([satelitte_images_2016_df, satelitte_images_2020_df, satelitte_images_2023_df], axis=0, ignore_index=True)

# Count the number of null values in each column
null_counts = satellite_images_combined_df.isnull().sum()

# Check if there are any null values
if null_counts.any():
    print("There are null values in the following columns:")
    print(null_counts[null_counts > 0])
else:
    print("There are no null values in any columns.")

# Save the combined DataFrame to a CSV file
satellite_images_combined_df.to_csv('US_County_Level_Satellite_Images_copy.csv', index=False)
