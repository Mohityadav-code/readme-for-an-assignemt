import requests
from bs4 import BeautifulSoup
import csv
import time
import pandas as pd

def fetch_and_process_data(url, year):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching data for {year}: {e}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', class_='ds-table')
    
    if not table:
        print(f"No table found for year {year}")
        return None
    
    rows = []
    for tr in table.find_all('tr')[1:]:
        row = []
        for td in tr.find_all('td'):
            text = td.text.strip()
            row.append(text)
        if row:
            row.append(str(year))
            rows.append(row)
    
    return rows

def analyze_ipl_stats(df):
    # Create player season participation map
    player_seasons = {}
    for year in range(2019, 2024):
        season_players = set(df[df['Year'] == year]['Player'])
        for player in season_players:
            if player not in player_seasons:
                player_seasons[player] = []
            player_seasons[player].append(year)

    # Filter players based on participation criteria
    qualified_players = set()
    for player, seasons in player_seasons.items():
        if 2019 in seasons and len([s for s in seasons if s in [2019, 2020, 2021]]) >= 3:
            qualified_players.add(player)
        elif len([s for s in seasons if s > 2019]) >= 2:
            qualified_players.add(player)

    # Calculate cumulative stats
    cumulative_stats = []
    for player in qualified_players:
        player_data = df[df['Player'] == player].sort_values('Year')
        
        cum_runs = 0
        cum_matches = 0
        cum_innings = 0
        cum_not_outs = 0
        cum_balls_faced = 0
        cum_fours = 0
        cum_sixes = 0
        cum_fifties = 0
        cum_hundreds = 0
        
        for _, season_data in player_data.iterrows():
            year = season_data['Year']
            
            cum_runs += int(season_data['Runs'])
            cum_matches += int(season_data['Mat'])
            cum_innings += int(season_data['Inns'])
            cum_not_outs += int(season_data['NO'])
            cum_balls_faced += int(season_data['BF'])
            cum_fours += int(season_data['4s'])
            cum_sixes += int(season_data['6s'])
            cum_fifties += int(season_data['50'])
            cum_hundreds += int(season_data['100'])
            
            cum_average = cum_runs / (cum_innings - cum_not_outs) if (cum_innings - cum_not_outs) > 0 else 0
            cum_strike_rate = (cum_runs / cum_balls_faced) * 100 if cum_balls_faced > 0 else 0
            
            cumulative_stats.append({
                'Player': player,
                'Year': year,
                'Cumulative_Matches': cum_matches,
                'Cumulative_Innings': cum_innings,
                'Cumulative_Runs': cum_runs,
                'Cumulative_Average': round(cum_average, 2),
                'Cumulative_Strike_Rate': round(cum_strike_rate, 2),
                'Cumulative_Fours': cum_fours,
                'Cumulative_Sixes': cum_sixes,
                'Cumulative_Fifties': cum_fifties,
                'Cumulative_Hundreds': cum_hundreds
            })

    # Get top 40 by cumulative runs for each season
    cum_df = pd.DataFrame(cumulative_stats)
    top_40_by_season = []
    
    for year in range(2019, 2024):
        season_stats = cum_df[cum_df['Year'] == year].nlargest(40, 'Cumulative_Runs')
        top_40_by_season.append(season_stats)
    
    final_df = pd.concat(top_40_by_season)
    return final_df

def main():
    # URLs for different years
    urls = {
        2019: "https://www.espncricinfo.com/records/tournament/batting-most-runs-career/indian-premier-league-2019-12741",
        2020: "https://www.espncricinfo.com/records/tournament/batting-most-runs-career/indian-premier-league-2020-21-13533",
        2021: "https://www.espncricinfo.com/records/tournament/batting-most-runs-career/indian-premier-league-2021-13840",
        2022: "https://www.espncricinfo.com/records/tournament/batting-most-runs-career/indian-premier-league-2022-14452",
        2023: "https://www.espncricinfo.com/records/tournament/batting-most-runs-career/indian-premier-league-2023-15129"
    }

    # Column headers
    headers = ['Player', 'Span', 'Mat', 'Inns', 'NO', 'Runs', 'HS', 'Ave', 'BF', 'SR', '100', '50', '0', '4s', '6s', 'Year']

    # Collect all data
    all_data = []
    for year, url in urls.items():
        print(f"Processing year {year}...")
        rows = fetch_and_process_data(url, year)
        if rows:
            all_data.extend(rows)
        time.sleep(2)

    # Create initial combined DataFrame
    df = pd.DataFrame(all_data, columns=headers)

    # Convert relevant columns to numeric
    numeric_columns = ['Mat', 'Inns', 'NO', 'Runs', 'BF', '4s', '6s', '50', '100']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Run the analysis
    result_df = analyze_ipl_stats(df)

    # Save both raw and analyzed data
    df.to_csv('ipl_batting_stats_raw.csv', index=False)
    result_df.to_csv('ipl_top_40_cumulative_stats.csv', index=False)

    print("\nAnalysis completed!")
    print(f"Raw data saved to: ipl_batting_stats_raw.csv")
    print(f"Top 40 cumulative stats saved to: ipl_top_40_cumulative_stats.csv")

    # Print some basic statistics
    print("\nBasic statistics:")
    print(f"Total qualified players: {len(set(result_df['Player']))}")
    print("\nNumber of players by season in top 40:")
    print(result_df['Year'].value_counts().sort_index())

if __name__ == "__main__":
    main()