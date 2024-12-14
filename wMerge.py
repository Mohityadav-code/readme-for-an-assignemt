import pandas as pd
import glob

# Get all CSV files matching the pattern
files = glob.glob('ipl_batting_stats_*.csv')

# Create empty list to store all dataframes
dfs = []

# Read each CSV file and append to the list
for file in files:
    df = pd.read_csv(file)
    year = file.split('_')[-1].replace('.csv', '')  # Extract year from filename
    if 'Year' not in df.columns:  # Add Year column if it doesn't exist
        df['Year'] = year
    dfs.append(df)

# Combine all dataframes
combined_df = pd.concat(dfs, ignore_index=True)

# Save combined data to a new CSV file
combined_df.to_csv('ipl_batting_stats_combined.csv', index=False)

print(f"Combined {len(files)} files into ipl_batting_stats_combined.csv")
print(f"Total records: {len(combined_df)}")