# take the json file and convert it to a csv file
# data scraped from https://apnews.com/article/olympics-2024-medal-winners-today-b9522fd1223ae6599569ffe1ee48cc62

import json
import pandas as pd
import regex as re

PARIS_PATH = "data/raw/paris2024_results.json"


SPORT_LIST = ["ATHLETICS",
              "BASKETBALL",
              "CYCLING TRACK",
              "HANDBALL",
              "MODERN PENTATHLON",
              "VOLLEYBALL",
              "WATER POLO",
              "WEIGHTLIFTING",
              "WRESTLING",
              "ARTISTIC SWIMMING",
              "BASKETBALL",
              "BEACH VOLLEYBALL",
              "BOXING",
              "BREAKING",
              "CANOE SPRINT",
              "CYCLING TRACK",
              "DIVING",
              "GOLF",
              "HANDBALL",
              "MODERN PENTATHLON",
              "RHYTHMIC GYMNASTICS",
              "SOCCER",
              "SPORT CLIMBING",
              "TABLE TENNIS",
              "TAEKWONDO",
              "TRACK AND FIELD",
              "VOLLEYBALL",
              "WATER POLO",
              "WEIGHTLIFTING",
              "WRESTLING",
              "TRACK AND FIELD",
              "BEACH VOLLEYBALL",
              "BOXING",
              "BREAKING",
              "CANOE SPRINT",
              "CYCLING TRACK",
              "DIVING",
              "FIELD HOCKEY",
              "MARATHON SWIMMING",
              "RHYTHMIC GYMNASTICS",
              "SAILING",
                "SOCCER",
                "SPORT CLIMBING",
                "TABLE TENNIS",
                "TAEKWONDO",
                "WEIGHTLIFTING",
                "WRESTLING",
                "TRACK AND FIELD",
                "CYCLING",
                "CANOE SLALOM",
                "FIELD HOCKEY",
                "MARATHON SWIMMING",
                "SPORTS CLIMBING",
                "DIVING",
                "SAILING",
                "WOMEN’S KITESURFING",
                "WEIGHTLIFTING",
                "WRESTLING",
                "ARTISTIC SWIMMING",
                "BOXING",
                "CLIMBING",
                "CYCLING MEN’S TEAM PURSUIT",
                "CYCLING WOMEN’S TEAM PURSUIT",
                "SAILING",
                "SKATEBOARDING",
                "TAEKWONDO",
                "TRACK AND FIELD",
                "WEIGHTLIFTING",
                "WRESTLING",
                "BOXING",
                "CYCLING TRACK",
                "DIVING",
                "EQUESTRIAN",
                "SKATEBOARDING",
                "TRACK AND FIELD",
                "WRESTLING",
                "MEN’S 3X3 BASKETBALL",
                "WOMEN’S 3X3 BASKETBALL",
                "BADMINTON",
                "CANOE SLALOM",
                "CYCLING TRACK",
                "GYMNASTICS",
                "SHOOTING",
                "SURFING",
                "TRACK AND FIELD",
                "TRIATHLON",
                "ARCHERY",
                "ARTISTIC GYMNASTICS",
                "BADMINTON",
                "CYCLING",
                "EQUESTRIAN",
                "FENCING",
                "GOLF",
                "SHOOTING",
                "MEN’S 1500M FREESTYLE",
                "MEN’S 4x100M MEDLEY RELAY",
                "TABLE TENNIS",
                "TENNIS",
                "TRACK AND FIELD",
                "ARCHERY",
                "ARTISTIC GYMNASTICS",
                "BADMINTON",
                "CYCLING",
                "EQUESTRIAN",
                "FENCING",
                "JUDO",
                "ROWING",
                "SAILING",
                "SHOOTING",
                "SWIMMING",
                "TABLE TENNIS",
                "TENNIS",
                "TRACK AND FIELD",
                "ARCHERY",
                "BADMINTON",
                "DIVING",
                "CYCLING BMX RACING",
                "EQUESTRIAN",
                "FENCING",
                "JUDO",
                "ROWING",
                "SAILING",
                "SHOOTING",
                "SWIMMING",
                "TENNIS",
                "TRACK AND FIELD",
                "TRAMPOLINE",
                "CANOE SLALOM",
                "FENCING",
                "GYMNASTICS",
                "JUDO",
                "ROWING",
                "SHOOTING",
                "SWIMMING",
                "TRACK AND FIELD",
                "GYMNASTICS",
                "CANOE",
                "CYCLING",
                "DIVING",
                "FENCING",
                "JUDO",
                "ROWING",
                "SWIMMING",
                "SHOOTING",
                "TRIATHLON",
                "FENCING",
                "GYMNASTICS",
                "JUDO",
                "RUGBY SEVENS",
                "SHOOTING",
                "SWIMMING",
                "TABLE TENNIS",
                "ARCHERY",
                "ARTISTIC GYMNASTICS",
                "CANOE SLALOM",
                "CYCLING MOUNTAIN BIKE",
                "DIVING",
                "EQUESTRIAN",
                "FENCING",
                "JUDO",
                "SHOOTING",
                "SKATEBOARDING",
                "SWIMMING",
                "ARCHERY",
                "CANOE SLALOM",
                "CYCLING MOUNTAIN BIKE",
                "FENCING",
                "JUDO",
                "SHOOTING",
                "SWIMMING",
                "SHOOTING",
                "SKATEBOARDING",
                "CYCLING",
                "DIVING",
                "FENCING",
                "JUDO",
                "RUGBY SEVENS",
                "SHOOTING",
                "SWIMMING",
                ]


def clean_paris_data(path):
    """Clean the json data and save it to a csv file"""
    data = load_data(path)
    
    # remove dates from h2 data
    h2_data = remove_dates_from_h2(data['h2'])
    # remove symbols from h2 data
    h2_data = remove_symbols_from_h2(h2_data)
    # combine the CYCLING and TEAM PURSUIT data
    h2_data = combine_cycling_pursuit(h2_data)
    # update the 3X3 BASKETBALL data
    h2_data = update_3x3_basketball(h2_data)
    # clean the SWIMMING RELAYS data
    h2_data = clean_swimming_relays(h2_data)
    
    # remove headlines from p data
    p_data = remove_headlines_from_p(data['p'])
    # clean medals events from p data
    p_data = clean_medals_events_from_p(p_data)
    
    data = {'h2': h2_data, 'p': p_data}
    
    # group the medals with the events
    grouped_medals = group_medals(data)
    # combine the grouped medals with the h2 data
    combined_data = combine_grouped_medals_with_h2(h2_data, grouped_medals)
    
    # geat the events from the p data
    p_events = get_p_events(p_data)
    
    # convert the cleaned data to a DataFrame
    df = convert_to_df(combined_data)
    
    # adjust the event and sports
    df = adjust_event_and_sports(df)
    
    # replace the sport names
    df = replace_sport(df)
    
    return df, p_events
    



def load_data(path):
    """Load in the json data from a file path"""
    with open(path) as f:
        data = json.load(f)
    return data





def remove_dates_from_h2(h2_data: list) -> list:
    """Remove any string values that are dates
    Example of string date removed is 'Sunday, Aug. 11'
    
    Args:
        h2_data (list): list of the h2 tag data from AP News website
    
    Returns:
        list: list of the h2 tag data with dates removed
    """

    # regex pattern to match day of the week
    day_of_week = re.compile(r"([A-Z][a-z]+day)")
    # create a copy of the data
    h2_list = h2_data.copy()

    for val in h2_data:
        # check if the value matches the regex pattern
        if day_of_week.match(val):
            h2_list.remove(val)
            
    return h2_list
    




def remove_symbols_from_h2(h2_data: list) -> list:
    """Keep only values that have some letters in them
    
    Args:
        h2_data (list): list of the h2 tag data from AP News website
    
    Returns:
        list: list of the h2 tag data with symbols removed
    """
    
    # create an empty list to store the updated data
    cleaned_h2_data = []

    # regex pattern to match any string with letters
    has_letters = re.compile(r"[a-zA-Z]")

    for val in h2_data:
        if val.startswith("3X3 BASKETBALL"):
            cleaned_h2_data.append(val)
        # check if the value matches the regex pattern
        elif not has_letters.match(val):
            continue
        else:
            cleaned_h2_data.append(val)
            
    return cleaned_h2_data




def combine_cycling_pursuit(h2_data: list) -> list:
    """The data for CYCLING and TEAM PURSUIT needs to be combined.
    
    Args:
        h2_data (list): list of the h2 tag data from AP News website
        
    Returns:
        list: list of the h2 tag data with CYCLING and TEAM PURSUIT combined
    """
    
    updated_h2_data = []
    
    for i, val in enumerate(h2_data):
        if val == "CYCLING" and "TEAM PURSUIT" in h2_data[i+1]:
            continue
            
        elif "TEAM PURSUIT" in val:
            updated_h2_data.append(f"CYCLING {val}")
            
        else:
            updated_h2_data.append(val)
    
    return updated_h2_data



def update_3x3_basketball(h2_data: list) -> list:
    """ The Women's 3X3 Basketball simply says WOMEN,
    this needs to be updated to WOMEN's 3X3 BASKETBALL and
    Men's 3X3 Basketball needs to be updated from 3X3 BASKETBALL
    to MEN'S 3X3 BASKETBALL"""

    updated_h2_data = []
    
    womens_index = None
    
    for i, val in enumerate(h2_data):
        if val == "3X3 BASKETBALL":
            updated_h2_data.append(f"MEN’S {val}")
            womens_index = i + 1
        elif womens_index == i:
            updated_h2_data.append("WOMEN’S 3X3 BASKETBALL")
        else:
            updated_h2_data.append(val)
            
    return updated_h2_data


def clean_swimming_relays(h2_data: list) -> list:
    
    updated_h2_data = []
    
    for i, val in enumerate(h2_data):
        if val == "SWIMMING" and "1500M" in h2_data[i+1]:
            updated_h2_data.append("WOMEN’S 50M FREESTYLE")
            updated_h2_data.append("WOMEN’S 4x100M MEDLEY RELAY")
        elif val == "MEN’S 1500M FREESTYLE":
            updated_h2_data.append(val)
            updated_h2_data.append("MEN’S 4x100M MEDLEY RELAY")
        else:
            updated_h2_data.append(val)
            
    return updated_h2_data




def remove_headlines_from_p(p_data: list) -> list:
    """ Remove any string values that are not events or results.
    Events are all uppercase strings.
    Results all start with either Gold, Silver, or Bronze.
    
    Args:
        p_data (list): list of the p tag data from AP News website
        
    Returns:    
        list: list of the p tag data with non-event and non-result strings removed
    """
        
    # create list for the results data
    results_data = []
        
    for val in p_data:
        # if the value is an all uppercase string, it is an event
        if val.isupper():
            results_data.append(val)
        # if the value starts with Gold, Silver, or Bronze, it is a result
        elif val.lower().startswith('gold:') or val.lower().startswith('silver:') or val.lower().startswith('bronze:'):
            results_data.append(val)
        # remove any events that slipped through the first check    
        elif val.lower().startswith('men') or val.lower().startswith('women'):   
            results_data.append(val)

    return results_data
            
            
            
            
def clean_medals_events_from_p(p_data: list) -> list:
    """Look if there are any values that are combined event and medal.
    Example: 'WOMEN'S MARATION Gold: Peres Jepchirchir, Kenya'
    This should be split into two separate values.
    
    Args:
        p_data (list): list of the p tag data from AP News website
        
    Returns:
        list: list of the p tag data with combined event and medal 
        strings split into two separate values
    """

    # new list of event results
    event_results = []
    
    # match string that has Gold, Silver, or Bronze but not at the start
    medals = re.compile(r"(?<!^)(Gold:|Silver:|Bronze:)")
    
    for val in p_data:
        # check if the value matches the regex pattern
        if medals.search(val):
            if "Gold:" in val:
                event, medal = val.split("Gold:")
                medal = "Gold:" + medal
                event_results.append(event.rstrip())
                event_results.append(medal)
            elif "Silver:" in val:
                event, medal = val.split("Silver:")
                medal = "Silver:" + medal
                event_results.append(event.rstrip())
                event_results.append(medal)
            elif "Bronze:" in val:
                event, medal = val.split("Bronze:")
                medal = "Bronze:" + medal
                event_results.append(event.rstrip())
                event_results.append(medal)
                
        else:
            event_results.append(val)
                
    return event_results

def get_p_events(p_data: list) -> list:
    """Get all the events from the p data
    
    Args:
        p_data (list): list of the p tag data from AP News website
        
    Returns:
        list: list of the events from the p data
    """
    
    events = []
    
    # events do not start with Gold, Silver, or Bronze
    no_medals = re.compile(r"^(?!Gold:|Silver:|Bronze:)")
    # iterate through the p data
    for val in p_data:
        # check if the value matches the regex pattern
        if no_medals.match(val):
            events.append(val)
            
    return events




def group_medals(data: dict) -> list:
    """Group the medals in a list and assign them to the event
    
    Args:
        data (dict): dictionary of the cleaned data
    Returns:
        list: list of the events and their respective medal winners
    """
    # create a dictionary to store the event and medal results
    event_results = []
    # create a list of medals
    medals_list = []

    for val in data["p"]:
        # if the value starts with Gold:
        if val.startswith("Gold:"):
            medals_list.append(val)
        # if the value starts with Silver:
        elif val.startswith("Silver:"):
            medals_list.append(val)
            # two exceptions where no Bronze medal was awarded
            if "Sofiane Oumiha, France" in val:
                medals_list.append("Bronze: No medal awarded")
                event_results.append(medals_list)
                medals_list = []
            elif "Nurbek Oralbay, Kazakhstan" in val:
                medals_list.append("Bronze: No medal awarded")
                event_results.append(medals_list)
                medals_list = []
            
        # if the value starts with Bronze:
        elif val.startswith("Bronze:"):
            if "Amin Mirzazadeh, Iran" in val:
                medals_list.append(val)
            elif "Zholaman Sharshenbekov, Kyrgyzstan" in val:
                medals_list.append(val)
            else:
                medals_list.append(val)
                event_results.append(medals_list)
                medals_list = []
                
    return event_results
        

        
    
def combine_grouped_medals_with_h2(h2_data: list, grouped_medals: list) -> list:
    
    assert len(h2_data) == len(grouped_medals)
    
    combined_data = [[x,y] for x,y in zip(h2_data, grouped_medals)]
    
    return combined_data
    
    
    
def convert_to_df(cleaned_data: list) -> pd.DataFrame:
    """Convert the cleaned data to a pandas DataFrame"""
    df = pd.DataFrame(cleaned_data, columns=["Sport", "Medal Winners"])
    
    # create a duplicate colum of Sport named Event
    df["Event"] = df["Sport"]


    return df
    
    
    
    

def adjust_event_and_sports(df: pd.DataFrame) -> pd.DataFrame:
    j = 0
    for i, row in df.iterrows():
        try:
            if row['Sport'] == SPORT_LIST[j]:
                j+=1
            else:
                df.loc[i, 'Sport'] = SPORT_LIST[j-1]
        except:
            continue
    return df


def replace_sport(df: pd.DataFrame) -> pd.DataFrame:
    df['Sport'] = df['Sport'].replace({'CYCLING MEN’S TEAM PURSUIT': 'CYCLING',
                                       'CYCLING WOMEN’S TEAM PURSUIT': 'CYCLING',
                                        'MEN’S 3X3 BASKETBALL': '3X3 BASKETBALL',
                                        'WOMEN’S 3X3 BASKETBALL': '3X3 BASKETBALL',
                                        'MEN’S 1500M FREESTYLE': 'SWIMMING',
                                        'MEN’S 4x100M MEDLEY RELAY': 'SWIMMING',
                                        'MEN’S 4X100M FREESTYLE RELAY': 'SWIMMING',
                                        'WOMEN’S 400M FREESTYLE': 'SWIMMING',
                                        'WOMEN’S 4X100M FREESTYLE RELAY': 'SWIMMING',})
    return df


def insert_p_events(df: pd.DataFrame, p_events: list) -> pd.DataFrame:
    temp_events = p_events.copy()
    
    j = 0
    for i, row in df.iterrows():
        if i == 28:
            df.loc[i, 'Event'] = "MEN’S"
        elif row['Sport'] == row['Event']:
            df.loc[i, 'Event'] = temp_events[j]
            j+=1
    return df
                 

############################################
# TESTING
############################################

def test_load_data():
    data = load_data(PARIS_PATH)
    assert type(data) == dict
    assert data.keys() == {'h2', 'p'}
    
    
def test_remove_dates_from_h2():
    test_data = ["Saturday, Aug. 10", "Sunday, Aug. 11", "Monday, Aug.12",
                       "BOXING", "Tuesday, Aug. 13", "Wednesday, Aug. 14", "Thursday, Aug. 15", "Friday, Aug. 16"]
    no_date = remove_dates_from_h2(test_data)
    assert no_date == ["BOXING"]
    
def test_remove_symbols_from_h2():
    test_data = [ "CYCLING", "3X3 BASKETBALL", "ATHLETICS", "_______", "BOXING", "######"]
    no_symbol = remove_symbols_from_h2(test_data)
    assert no_symbol == ["CYCLING", "3X3 BASKETBALL", "ATHLETICS", "BOXING"]
    
    
def test_remove_headlines_from_p():
    test_data = ["PARIS (AP) — The 2024 Olympics are done. The United States led the final medal standings with 126 total medals, ahead of China (91), Britain (65) and France (64). Below is a list of all the medal winners, day by day.",
                        "\n",
                        "2024 Paris Olympics:",
                        "▶ See other events still in progress",
                        "GOLD: Tom Pidcock, Britain",
                        "WOMEN’S 500M SINGLE KAYAK",]
    no_headlines = remove_headlines_from_p(test_data)
    assert no_headlines == ["GOLD: Tom Pidcock, Britain", "WOMEN’S 500M SINGLE KAYAK"]


def test_clean_medals_events():
    test_data = ["MEN’S 90KG Gold: Lasha Bekauri, Georgia"]
    cleaned_data = clean_medals_events_from_p(test_data)
    assert cleaned_data == ["MEN’S 90KG", "Gold: Lasha Bekauri, Georgia"]
    
    
def test_update_3x3_basketball():
    test_data = ["MEN’S GRECO-ROMAN 60KG",
                "WOMEN’S FREESTYLE 68KG",
                "3X3 BASKETBALL",
                "WOMEN",
                "BADMINTON"]
    updated_data = update_3x3_basketball(test_data)
    assert updated_data == ["MEN’S GRECO-ROMAN 60KG",
                            "WOMEN’S FREESTYLE 68KG",
                            "MEN’S 3X3 BASKETBALL",
                            "WOMEN’S 3X3 BASKETBALL",
                            "BADMINTON"]
    
    
def test_clean_swimming_relays():
    test_data = ["SWIMMING",
                "MEN’S 1500M FREESTYLE"]
    cleaned_data = clean_swimming_relays(test_data)
    assert cleaned_data == ["WOMEN’S 50M FREESTYLE",
                            "WOMEN’S 4x100M MEDLEY RELAY",
                            "MEN’S 1500M FREESTYLE",
                            "MEN’S 4x100M MEDLEY RELAY"]
    
    
def test_get_p_events():
    test_data = ["WOMEN’S MARATHON",
                "Gold: Netherlands (Sifan Hassan)",
                "Silver: Ethiopia (Tigst Assefa)",
                "Bronze: Kenya (Hellen Obiri)",
                "WOMEN’S",
                "Gold: United States",
                "Silver: France",
                "Bronze: Australia",
                "MEN’S KEIRIN",
                "Gold: Netherlands (Harrie Lavreysen)",
                "Silver: Australia (Matthew Richardson)",
                "Bronze: Australia (Matthew Glaetzer",
                "WOMEN’S 3X3 BASKETBALL Gold: United States",
                ]
    events = get_p_events(test_data)
    assert events == ["WOMEN’S MARATHON",
                      "WOMEN’S",
                        "MEN’S KEIRIN",
                        "WOMEN’S 3X3 BASKETBALL Gold: United States"] 
    
    