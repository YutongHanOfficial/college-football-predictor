import csv
import re
from datetime import datetime

def parse_ncaa_scores(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    games = []
    current_date = "2026-08-29"
    i = 0

    while i < len(lines):
        line = lines[i]

        # Detect Date Header (e.g., "SATURDAY, AUGUST 29, 2026")
        if re.match(r"^[A-Z]+, [A-Z]+ \d{1,2}, \d{4}$", line):
            try:
                dt = datetime.strptime(line, "%A, %B %d, %Y")
                current_date = dt.strftime("%Y-%m-%d")
            except ValueError:
                pass
            i += 1
            continue

        # Stop parsing when reaching page footers/links
        if "FBS FOOTBALL" in line or "NCAA Footer" in line:
            break

        if line == "FINAL":
            i += 1
            
            # Helper function to read one team's entry (Rank, Name, Score)
            def parse_team_block(idx):
                # If a line is digits and the line AFTER it is NOT digits, it's an AP Rank
                if lines[idx].isdigit() and idx + 1 < len(lines) and not lines[idx + 1].isdigit():
                    idx += 1  # Skip rank
                
                team_name = lines[idx]
                idx += 1
                
                score = int(lines[idx])
                idx += 1
                
                return team_name, score, idx

            try:
                # NCAA always lists Away Team first, Home Team second
                away_team, away_score, i = parse_team_block(i)
                home_team, home_score, i = parse_team_block(i)
                
                games.append([current_date, home_team, away_team, home_score, away_score])
            except (IndexError, ValueError):
                break
        else:
            i += 1

    # Write output CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["date", "home", "away", "home_score", "away_score"])
        writer.writerows(games)

    print(f"✅ Successfully converted {len(games)} games to {output_file}")

# Execute
parse_ncaa_scores('ncaa_raw.txt', 'games_2026.csv')
