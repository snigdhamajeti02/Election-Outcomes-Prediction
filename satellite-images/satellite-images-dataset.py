import os
import pandas as pd
import geopandas as gpd

year = 2016

# Path to the downloaded and unzipped shapefile
shapefile_path = f'cbp-datasets/cb_{year}_us_county_500k'

# Load the shapefile into a GeoDataFrame
counties = gpd.read_file(shapefile_path)

# Drop the geometry column and sort by 'GEOID'
counties_df = counties.drop(columns='geometry').sort_values(by='GEOID').reset_index(drop=True)

# Convert 'GEOID' to FIPS code and create modified name for image
counties_df['fips'] = pd.to_numeric(counties_df['GEOID'], errors='coerce', downcast='integer')
counties_df['modified_name'] = counties_df['NAME'].str.replace(" ", "_").str.replace(",", "").str.replace(":", "").str.replace("/", "_")
counties_df['image_name'] = counties_df['modified_name'] + '_' + counties_df['GEOID']

# Filter for FIPS codes < 60000
counties_df = counties_df[counties_df['fips'] < 60000]

# Set folder path and filter image names that exist in the directory
folder = f'{year}-US-Counties-Images-500k'
image_names = [image_name.replace('.jpg', '') for image_name in os.listdir(folder)]

# Filter counties where image names exist
counties_df = counties_df[counties_df['image_name'].isin(image_names)]

# Select relevant columns and reset index
counties_df = counties_df[['fips', 'ALAND', 'AWATER', 'image_name']].reset_index(drop=True)

# Convert 'fips' to integer type
counties_df['fips'] = counties_df['fips'].astype('int64')

# Define the CSV file path and save the DataFrame
csv_name = f'US_County_{year}_Satellite_Images.csv'
counties_df.to_csv(csv_name, index=False)
