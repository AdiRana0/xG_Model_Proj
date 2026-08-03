import pandas as pd
import numpy as np
import ast
import json
import joblib

# --- READ DATA ---

shots_DF = pd.read_csv('data/raw_shots.csv')
# print(shots_DF.shape)
# print(shots_DF[['location', 'shot_technique', 'shot_body_part', 'shot_outcome']].head())
# print(shots_DF['location'].dtype)


# --- EXTRACT LOCATION ---


# Break all location strings into separate coordinate values x and y and store in DF
shots_DF[['x', 'y']] = shots_DF['location'].apply(
    lambda loc: pd.Series(ast.literal_eval(loc))
)
# print(shots_DF[['location', 'x', 'y']]).head


# --- CALCULATE DISTANCE AND ANGLE ---


GOAL_X = 120
GOAL_Y = 40
POST_L = 36     # Posts are same x value, 
POST_R = 44     # and +-4 offset applied to GOAL_Y


def distance(x, y):
    return np.sqrt( (GOAL_X - shots_DF['x'])**2 + (GOAL_Y - shots_DF['y'])**2 )


def angle(x, y):
    angle_top = np.arctan2(POST_L - y, GOAL_X - x)
    angle_bottom = np.arctan2(POST_R - y, GOAL_X - x)
    return np.abs(angle_top - angle_bottom)



shots_DF['distance'] = distance(shots_DF['x'], shots_DF['y'])
# Distance is length of straight line from position of the ball to dead center of goal

shots_DF['angle'] = np.degrees(angle(shots_DF['x'], shots_DF['y']))
# Angle between lines formed from ball to either goal post; represents width of the visible goal 

# print(shots_DF[['x', 'y', 'distance', 'angle']])


# --- STORE BINARY OUTCOME ---

def is_goal(s):
    if (s == 'Goal'): return 1
    return 0


shots_DF['is_goal'] = shots_DF['shot_outcome'].apply(is_goal)
# Stores 1 for goal and 0 for all other outcomes; binary representation

# print(shots_DF[['x', 'y', 'distance', 'angle', 'is_goal']].head(20))
# print(shots_DF['is_goal'].sum()) # total number of goals 


# --- CONVERT BOOL FLAGS TO BINARY ---

bool_flags = ['under_pressure', 'shot_first_time', 'shot_one_on_one']

for col in bool_flags:
    shots_DF[col] = shots_DF[col].notna().astype(int)
    # Replace all NaN with 0

# print(shots_DF[['under_pressure', 'shot_first_time', 'shot_one_on_one']])


# --- HANDLE CATEGORICAL COLUMNS ---

cat_cols = ['shot_technique', 'shot_body_part', 'shot_type'] 

shots_DF = pd.get_dummies(shots_DF, columns=cat_cols) 
# Each cat_col is broken into multiple cols, one for each possible value
# Ex. shot_technique col is replaced with binary cols for normal, volley, header, etc.


# --- FEATURES AND LABEL ---

feature_cols = ['distance', 'angle', 'under_pressure', 'shot_one_on_one', 'shot_first_time'] + \
[col for col in shots_DF.columns if col.startswith(('shot_technique', 'shot_body_part', 'shot_type'))]

X = shots_DF[feature_cols]
y = shots_DF['is_goal']

# print(f"Features: {X.columns}")
# print(f"Label: {y.name}")

joblib.dump((X, y), 'data/Xy.pkl') 
# Save X and y

with open('data/X_cols.json', 'w') as f: json.dump(feature_cols, f)
# Save col format of X for UI
