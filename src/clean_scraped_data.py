### Data Check:
# According to ChatGPT there were 33 sports and 339 medaling events in Tokyo 2020.
# And 329 medaling events across 45 different sports in Paris 2024 and 206 countries in Paris.


import pandas as pd
import json
import regex as re


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


final_tokyo_df = pd.DataFrame(
    columns=["Athlete", "NOC", "Year", "Season", "City", "Sport", "Event", "Medal"]
)

# Create the list of medals
medals = ["Gold", "Silver", "Bronze"]


# iterate through the rows and extract the team, noc and medal
# from the results column and add them to the final dataframe
for i, row in tokyo_df.iterrows():
    sport = row["Sport"]
    event = row["Event"]
    results = row["Results"]
    
    
def create_event_df(df_row: pd.Series) -> pd.DataFrame:
    """Takes in a row from the Tokyo 2020 dataframe and creates a new dataframe
    with the athlete, noc, year, season, city, sport, event and medal columns.
    
    Args:
        df_row (pd.Series): A row from the Tokyo 2020 dataframe.
        
    Returns:
        pd.DataFrame: A new dataframe with the athlete, noc, year, season, city, sport, event and medal columns.
    """
    
    sport = df_row["Sport"]
    event = df_row["Event"]
    results = df_row["Results"]
    
    # create a list of the athletes and their respective NOC
    medal_tuple = split_medals(results)
    gold, silver, bronze = medal_tuple[0], medal_tuple[1], medal_tuple[2]
    
    # create a list of the medals
    medals = ["Gold", "Silver", "Bronze"]
    
    # create a list of the final columns
    columns = ["Athlete", "NOC", "Year", "Season", "City", "Sport", "Event", "Medal"]
    

    return -1
    
    
    
    
def split_medals(results: list)-> tuple:
    """Takes in a list of athlete names and/or NOC to parse.
    The list is of the results from the event and uses the order in the list
    to signify which medal it is. 
    
    There is a mix of team events and individual events. This makes the parsing
    more complex. As well, if there is a tie in an individual event, then there
    will be a different ordering of the values.
    
    
    Returns with a list of either team or individual with country (NOC).
    Team Example:
        (['USA'], ['CAN'], ['GBR'])
    
    Individual Example:
        (["Michael Phelps", "USA"], ["Ryan Lochte", "USA"], ["Laszlo Cseh", "HUN"])
    
    Example:
        Team Results: 
            
            ['USA', 'CAN', 'GBR'] 
            This would Gold for USA, Silver for CAN and Bronze for GBR
            
            Assumption: There will be no ties in team events.
            
        Individual Results: 
        
            ["Michael Phelps", "USA", "Ryan Lochte", "USA", "Laszlo Cseh", "HUN"] 
            This would be Gold for Michael Phelps, Silver for Ryan Lochte and Bronze for Laszlo Cseh

        If there is a tie for gold then the results would be:
        
            ["Michael Phelps", "Ryan Lochte", "USA", "USA", "Laszlo Cseh", "HUN"]
            This would be Gold for Michael Phelps, Silver for Ryan Lochte and Laszlo Cseh an no Bronze.
        
        If there is a tie for silver then the results would be:
            
            ["Michael Phelps", "USA", "Ryan Lochte", "Laszlo Cseh", "USA", "HUN"]
            This would be Gold for Michael Phelps, Silver for Ryan Lochte and Laszlo Cseh an no Bronze.
        
        If there is a tie for bronze then the results would be:
            
            ["Michael Phelps", "USA", "Ryan Lochte", "USA", "Laszlo Cseh", "Chad Le Clos", "HUN", "RSA"]
            This would be Gold for Michael Phelps, Silver for Ryan Lochte and tie for Bronze between
            Laszlo Cseh and Chad Le Clos.
    
    """

    # create a regex for the country
    country_regex = re.compile(r"[A-Z]{3}")
    
    country_indices = [i for i, x in enumerate(results) if country_regex.match(x)]
    
    if country_indices == [0,1,2]:
        gold = [results[0]]
        silver = [results[1]]
        bronze = [results[2]]
    elif country_indices == [1,3,5]:
        gold = results[:2]
        silver = results[2:4]
        bronze = results[4:]
    # tie for gold indices
    elif country_indices == [2,3,5]:
        gold = results[:4]
        silver = []
        bronze = results[4:] 
    # tie for silver indices
    elif country_indices == [1,4,5]:
        gold = results[:2]
        silver = results[2:]
        bronze = []   
    # tie for bronze indices
    else:
        gold = results[:2]
        silver = results[2:4]
        bronze = results[4:] 
    
    
    return gold, silver, bronze
        


def test_simple_split_medals():
    # Test the split_medals function
    results = ['USA', 'CAN', 'GBR']
    assert split_medals(results) == (['USA'], ['CAN'], ['GBR'])
    
    results = ["Michael Phelps", "USA", "Ryan Lochte", "USA", "Laszlo Cseh", "HUN"]
    assert split_medals(results) == (["Michael Phelps", "USA"], ["Ryan Lochte", "USA"], ["Laszlo Cseh", "HUN"])
    

def test_gold_tie():
    results = ["Michael Phelps", "Ryan Lochte", "USA", "USA", "Laszlo Cseh", "HUN"]
    assert split_medals(results) == (["Michael Phelps", "Ryan Lochte", "USA", "USA"], [], ["Laszlo Cseh", "HUN"])
    
def test_silver_tie():
    results = ["Michael Phelps", "USA", "Ryan Lochte", "Laszlo Cseh", "USA", "HUN"]
    assert split_medals(results) == (["Michael Phelps", "USA"], ["Ryan Lochte", "Laszlo Cseh", "USA", "HUN"], [])
    
def test_bronze_tie():
    results = ["Michael Phelps", "USA", "Ryan Lochte", "USA", "Laszlo Cseh", "Chad Le Clos", "HUN", "RSA"]
    assert split_medals(results) == (["Michael Phelps", "USA"], ["Ryan Lochte", "USA"], ["Laszlo Cseh", "Chad Le Clos", "HUN", "RSA"])
    
    
def test_event_df():
    test_df = pd.DataFrame({"Sport": ["Swimming"], 
                            "Event": "100M Freestyle (Men)", 
                            "Results": ["Caeleb Dressel", "USA", "Kyle Chalmers", "AUS", "Kliment Kolesnikov", "ROC"]})
    
    final_df = create_event_df(test_df)
    assert final_df.shape == (3, 8)
    assert final_df["Sport"].unique() == ["Swimming"]
    assert final_df[final_df["Medal"] == ["Gold"]]["Athlete"].values == ["Caeleb Dressel"]
    assert final_df[final_df["Medal"] == ["Silver"]]["Athlete"].values == ["Kyle Chalmers"]
    assert final_df[final_df["Medal"] == ["Bronze"]]["Athlete"].values == ["Kliment Kolesnikov"]