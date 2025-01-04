import pandas as pd

# Function to load and clean 2016 election data
def load_and_clean_2016_data(file_path):
    df = pd.read_csv(file_path)
    df = df.drop(columns='Unnamed: 0')

    # Remove duplicates
    df = df[~df.duplicated(subset=['votes_dem', 'votes_gop', 'total_votes', 'per_dem', 'per_gop', 'diff', 'per_point_diff', 'state_abbr', 'county_name'], keep='first')]

    # Reorder columns specific to 2016
    new_order = ['state_abbr', 'combined_fips', 'county_name', 'votes_gop', 'votes_dem', 'total_votes', 'diff', 'per_gop', 'per_dem', 'per_point_diff']
    df = df[new_order]

    # Map state abbreviations to full names
    state_abbr_to_full = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
        'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
        'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
        'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts',
        'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana',
        'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico',
        'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
        'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota',
        'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington',
        'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia', 'GU': 'Guam',
        'MP': 'Northern Mariana Islands', 'VI': 'Virgin Islands', 'AS': 'American Samoa', 'PR': 'Puerto Rico', 'TT': 'Trust Territories',
    }

    # Apply mapping and column renaming
    df['state_abbr'] = df['state_abbr'].map(state_abbr_to_full)
    df.rename(columns={'combined_fips': 'county_fips', 'state_abbr': 'state_name'}, inplace=True)

    # Sort by county FIPS and reset index
    df = df.sort_values(by='county_fips').reset_index(drop=True)

    # Insert year and convert column types
    df.insert(0, 'year', 2016)
    df['votes_gop'] = df['votes_gop'].astype('int64')
    df['votes_dem'] = df['votes_dem'].astype('int64')
    df['total_votes'] = df['total_votes'].astype('int64')
    df['diff'] = df['diff'].str.replace(',', '').astype('float64')
    df['per_point_diff'] = df['per_point_diff'].str.replace('%', '').astype('float64')

    return df

# Function to load and clean 2020 and 2024 election data (same processing for both)
def load_and_clean_2020_2024_data(file_path, year):
    df = pd.read_csv(file_path)

    # Remove duplicates
    df = df[~df.duplicated(subset=['state_name', 'county_fips', 'county_name', 'votes_gop', 'votes_dem', 'total_votes', 'diff', 'per_gop', 'per_dem', 'per_point_diff'], keep='first')]

    # Insert year and apply type conversion
    df.insert(0, 'year', year)
    df['votes_gop'] = df['votes_gop'].astype('int64')
    df['votes_dem'] = df['votes_dem'].astype('int64')
    df['total_votes'] = df['total_votes'].astype('int64')

    # Format and adjust per_point_diff for 2020 and 2024 data
    df['per_point_diff'] = (df['per_point_diff'] * 100).round(2)

    return df

# Load and clean all datasets
election_results_2016_df = load_and_clean_2016_data('2016_US_County_Level_Presidential_Results.csv')
election_results_2020_df = load_and_clean_2020_2024_data('2020_US_County_Level_Presidential_Results.csv', 2020)
election_results_2024_df = load_and_clean_2020_2024_data('2024_US_County_Level_Presidential_Results.csv', 2024)

# Combine all data
election_results_combined_df = pd.concat([election_results_2016_df, election_results_2020_df, election_results_2024_df], axis=0, ignore_index=True)

# Take absolute values for 'diff' and 'per_point_diff'
election_results_combined_df['diff'] = election_results_combined_df['diff'].abs()
election_results_combined_df['per_point_diff'] = election_results_combined_df['per_point_diff'].abs()

# Remove duplicates from the combined dataset
election_results_combined_df = election_results_combined_df[~election_results_combined_df.duplicated(subset=['year', 'state_name', 'county_fips', 'county_name', 'votes_gop', 'votes_dem', 'total_votes', 'diff', 'per_gop', 'per_dem', 'per_point_diff'], keep='first')]

# Check for null values and print the result
null_counts = election_results_combined_df.isnull().sum()
if null_counts.any():
    print("There are null values in the following columns:")
    print(null_counts[null_counts > 0])
else:
    print("There are no null values in any columns.")

# Save the combined dataset to a CSV
election_results_combined_df.to_csv('US_County_Level_Presidential_Results.csv', index=False)
