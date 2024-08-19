### Data Check:
# According to ChatGPT there were 33 sports and 339 medaling events in Tokyo 2020.
# And 329 medaling events across 45 different sports in Paris 2024 and 206 countries in Paris.


import pandas as pd
import json


KAGGLE_OLYMPICS = "../data/raw/olympics_1896_2016_data.csv"
TOKYO_2020 = "../data/raw/tokyo2020_medals.json"
PARIS_2024 = "../data/raw/paris2024_medals.json"

TOKYO_YEAR = "2020"
TOKYO_SEASON = "Summer"
TOKYO_CITY = "Tokyo"


def process_kaggle_olympics_data(file_path: str) -> pd.DataFrame:
    """Takes in the path to the kaggle olympics data.
    This is data from 1896 to 2016 and includes Summer and Winter Olympics.
    The function only keeps medaling rows and is only interested in Summer Olympics.
    Also, this function only keeps the winning country and specific event.

    Args:
        file_path (str): file path to the kaggle olympics data. This is a csv file.

    Returns:
        pd.DataFrame: A cleaned dataframe with columns
        ['Team', 'NOC', 'Year', 'Season', 'City', 'Sport', 'Event', 'Medal']
    """

    # create a list of the final columns to keep
    columns = ["Team", "NOC", "Year", "Season", "City", "Sport", "Event", "Medal"]
    # load old olympic data
    old_df = pd.read_csv(file_path)
    # remove the non-medal rows
    old_df = old_df[old_df["Medal"].notnull()]
    # create the final dataframe
    final_summer_df = old_df[columns]

    return final_summer_df


# Load the json file
with open(TOKYO_2020) as f:
    data_tokyo = json.load(f)


sports = list()
events = list()
medals = list()

# iterate through the keys (Sport) and results
for key, val in data_tokyo.items():
    sport = key
    for event, results in val.items():
        sports.append(sport)
        events.append(event)
        medals.append(results)

# create a dataframe
tokyo_df = pd.DataFrame({"Sport": sports, "Event": events, "Results": medals})

tokyo_df["Team"] = None
tokyo_df["NOC"] = None

final_tokyo_df = pd.DataFrame(
    columns=["Team", "NOC", "Year", "Season", "City", "Sport", "Event", "Medal"]
)

# Create the list of medals
medals = ["Gold", "Silver", "Bronze"]

# Repeat each sport/event combination for each medal
df_expanded = tokyo_df.loc[tokyo_df.index.repeat(3)].reset_index(drop=True)

# drop the results column
df_expanded.drop(columns="Results", inplace=True)

# Assign the medals to the new 'medal' column
df_expanded["Medal"] = medals * (len(df_expanded) // 3)

df_expanded

# iterate through the rows and extract the team, noc and medal
# from the results column and add them to the final dataframe
for i, row in tokyo_df.iterrows():
    sport = row["Sport"]
    event = row["Event"]
    results = row["Results"]
    # split the results into gold, silver and bronze
    split_val = len(results) // 3
    gold = results[:split_val]
    silver = results[split_val : 2 * split_val]
    bronze = results[2 * split_val :]
