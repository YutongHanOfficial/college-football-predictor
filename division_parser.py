import csv
import requests
import streamlit as st

DIV_LABELS = {
    'fbs': 'FBS',
    'fcs': 'FCS',
    'ii': 'D2',
    'iii': 'D3'
}

@st.cache_data(ttl=86400)  # Cache API classifications for 24 hours
def fetch_division_map(years):
    """Pulls NCAA classifications from CFBD API securely via Streamlit secrets."""
    api_key = st.secrets.get("CFBD_API_KEY", "")
    division_map = {}
    
    if not api_key:
        st.error("CFBD_API_KEY not found in Streamlit Secrets.")
        return division_map

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    for year in years:
        url = f"https://api.collegefootballdata.com/teams?year={year}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                division_map[str(year)] = {}
                for team in data:
                    school = team.get('school')
                    classification = team.get('classification', 'unknown').lower()
                    clean_div = DIV_LABELS.get(classification, classification.upper())
                    if school:
                        division_map[str(year)][school] = clean_div
        except Exception as e:
            st.warning(f"Could not fetch {year} divisions from API: {e}")

    return division_map

@st.cache_data
def get_tagged_games():
    """Reads CSV files and dynamically assigns year-accurate divisions in-memory."""
    years = ["2025", "2026"]
    division_map = fetch_division_map(years)
    all_games = []

    for year in years:
        file_path = f"games_{year}.csv"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)
                
                # Identify index positions
                date_idx = 0
                home_idx = 1
                
                for row in reader:
                    if not row:
                        continue
                    home_team = row[home_idx]
                    
                    # Dynamically look up team division for that year
                    div = division_map.get(year, {}).get(home_team, "UNKNOWN")
                    
                    # Attach division status
                    row_data = {
                        "date": row[0],
                        "home_team": row[1],
                        "away_team": row[2],
                        "home_score": row[3] if len(row) > 3 else None,
                        "away_score": row[4] if len(row) > 4 else None,
                        "division": div,
                        "season": year
                    }
                    all_games.append(row_data)
        except FileNotFoundError:
            continue

    return all_games
