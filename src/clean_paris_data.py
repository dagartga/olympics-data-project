# take the json file and convert it to a csv file

import json
import pandas as pd
import regex as re

PARIS_PATH = "data/raw/paris2024_results.json"




def clean_paris_data(path):
    """Clean the json data and save it to a csv file"""
    data = load_data(path)
    
    # remove dates from h2 data
    h2_data = remove_dates_from_h2(data['h2'])
    # remove symbols from h2 data
    h2_data = remove_symbols_from_h2(h2_data)
    
    # remove headlines from p data
    p_data = remove_headlines_from_p(data['p'])
    # clean medals events from p data
    p_data = clean_medals_events_from_p(p_data)
    
    data = {'h2': h2_data, 'p': p_data}
    
    return data
    



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
    # regex pattern to match any string with letters
    has_letters = re.compile(r"[a-zA-Z]")

    for val in h2_data:
        # check if the value matches the regex pattern
        if not has_letters.match(val):
            h2_data.remove(val)
            
    return h2_data





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
    test_data = [ "CYCLING", "ATHLETICS", "_______", "BOXING", "######"]
    no_symbol = remove_symbols_from_h2(test_data)
    assert no_symbol == ["CYCLING", "ATHLETICS", "BOXING"]
    
    
def test_remove_headlines_from_p():
    test_data = ["PARIS (AP) — The 2024 Olympics are done. The United States led the final medal standings with 126 total medals, ahead of China (91), Britain (65) and France (64). Below is a list of all the medal winners, day by day.",
                        "\n",
                        "2024 Paris Olympics:",
                        "▶ See other events still in progress",
                        "GOLD: Tom Pidcock, Britain",
                        "WOMEN'S 500M SINGLE KAYAK",]
    no_headlines = remove_headlines_from_p(test_data)
    assert no_headlines == ["GOLD: Tom Pidcock, Britain", "WOMEN'S 500M SINGLE KAYAK"]


def test_clean_medals_events():
    test_data = ["MEN’S 90KG Gold: Lasha Bekauri, Georgia"]
    cleaned_data = clean_medals_events_from_p(test_data)
    assert cleaned_data == ["MEN’S 90KG", "Gold: Lasha Bekauri, Georgia"]
    
    
