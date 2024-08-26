# take the json file and convert it to a csv file

import json
import pandas as pd
import regex as re

PARIS_PATH = "data/raw/paris2024_results.json"

def load_data(path):
    """Load in the json data from a file path"""
    with open(path) as f:
        data = json.load(f)
    return data

def remove_dates(data: dict) -> dict:
    """Remove any string values that are dates
    Example of string date removed is 'Sunday, Aug. 11'
    
    Args:
        data (dict): dictionary of data
    
    Returns:
        dict: dictionary with dates removed
    """

    # regex pattern to match day of the week
    day_of_week = re.compile(r"([A-Z][a-z]+day)")

    for val in data['h2']:
        # check if the value matches the regex pattern
        if day_of_week.match(val):
            data['h2'].remove(val)
            
    return data
    

def remove_symbols(data: dict) -> dict:
    """Keep only values that have some letters in them"""

    # regex pattern to match any string with letters
    has_letters = re.compile(r"[a-zA-Z]")

    for val in data['h2']:
        # check if the value matches the regex pattern
        if not has_letters.match(val):
            data['h2'].remove(val)
            
    return data



############################################
# TESTING
############################################

def test_load_data():
    data = load_data(PARIS_PATH)
    assert type(data) == dict
    assert data.keys() == {'h2', 'p'}
    
