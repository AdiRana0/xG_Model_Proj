from statsbombpy import sb
import pandas as pd

# --- ALL COMPETITIONS ---

competitions = sb.competitions() # pulls all the competitions stored in sb
# print(competitions[['competition_name', 'competition_id', 'season_name', 'season_id']])


# --- PL 2015/16 ---

COMP_ID = 2
SEASON_ID = 27

# Pulls all 380 matches from the 2015/16 PL Season:
matches = sb.matches(competition_id=COMP_ID, season_id=SEASON_ID)
# print(matches[['match_id', 'home_team', 'away_team', 'match_date']])


# --- TEST MATCH --- 
# Chelsea (H) vs Arsenal (A), id=3754217

test_events = sb.events(match_id=3754217) # all events from the test match
test_shots = test_events[test_events['type'] == 'Shot'] # all shots from the test match

# Display all the shots taken from the selected test match:
# print(test_shots[['location', 'shot_technique', 'shot_body_part', 'shot_one_on_one', 'under_pressure', 'shot_first_time', 'shot_outcome', 'shot_statsbomb_xg']])


# --- DATA ---
# Relevant info from all shots taken in the 2015-16 BPL season

MATCH_IDs = matches['match_id'].tolist()
print(f"Found {len(MATCH_IDs)} games") # all 380 games

all_shots = []

# pull shots from each match and add to all_shots
for i, match_id in enumerate(MATCH_IDs):
    events = sb.events(match_id=match_id)
    shots = events[events['type'] == 'Shot']
    shots['match_id'] = match_id  # store match_id to traceback each shot if needed 
    all_shots.append(shots)
    print(f"Added {len(shots)} shots from match {match_id}")

# Add all shots into single df
shots_DF = pd.concat(all_shots, ignore_index=True)
print(f"Total shots: {len(shots_DF)}")

# Save the pulled data
shots_DF.to_csv('data/raw_shots.csv', index=False)