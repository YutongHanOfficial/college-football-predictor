import csv
import requests
import time

# Your CFBD API key is passed as a Bearer token in the Authorization header.
API_KEY = "ic9heJuiVZLtkEtrWPEuzp/NMH4hNkE0fll6czlyEyt9CafX+/s64khHGLdzQnLB"

DIV_LABELS = {
    'fbs': 'FBS',
    'fcs': 'FCS',
    'ii': 'D2',
    'iii': 'D3'
}

def fetch_divisions(years):
    """Builds a master dictionary of team divisions pulled directly from the CFBD API."""
    division_map = {}
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    for year in years:
        print(f"Fetching {year} NCAA classifications...")
        url = f"https://api.collegefootballdata.com/teams?year={year}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            division_map[str(year)] = {}
            
            for team in data:
                school = team.get('school')
                classification = team.get('classification', 'unknown').lower()
                clean_div = DIV_LABELS.get(classification, classification.upper())
                
                if school:
                    division_map[str(year)][school] = clean_div
        else:
            print(f"API Error {year}: Status Code {response.status_code}")
            
        # Respect API limits by pausing slightly between year requests
        time.sleep(0.5) 
        
    return division_map

def build_categorized_dataset(input_file, output_file, division_map):
    """Parses raw games and appends correct divisions based on the year played."""
    output_rows = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        
        # Append 'division' to header if it isn't already there
        if header[-1].lower() != 'division':
            header.append('division')
        output_rows.append(",".join(header))
        
        for row in reader:
            date = row[0]
            year = date.split("-")[0]
            home_team = row[1]
            
            # Lookup the division dynamically. Defaults to UNKNOWN if a team isn't found.
            div = division_map.get(year, {}).get(home_team, "UNKNOWN")
            
            if len(row) == len(header):
                row[-1] = div # Overwrite existing incorrect division
            else:
                row.append(div) # Append new division
                
            output_rows.append(",".join(row))
            
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        f.write("\n".join(output_rows))
    print(f"Success! Categorized data saved to {output_file}")

if __name__ == "__main__":
    # Scan years 2025 and 2026 to capture the North Dakota St. transition automatically
    required_years = ["2025", "2026"] 
    
    master_map = fetch_divisions(required_years)
    build_categorized_dataset('raw_games.csv', 'categorized_games.csv', master_map)
