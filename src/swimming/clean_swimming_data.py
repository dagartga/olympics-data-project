import pandas as pd

OLYMPICS_DATA_PATH = "../../data/processed/all_olympics_data.csv"

def extract_swimming_data(file_path: str) -> pd.DataFrame:
    """Extracts swimming data from the all olympics data csv file.

    Args:
        file_path (str): file path to the all olympics data csv file.

    Returns:
        pd.DataFrame: A dataframe with only swimming data.
    """

    # load the all olympics data
    all_data = pd.read_csv(file_path)
    # filter out only swimming data
    swimming_data = all_data[all_data["Sport"].str.lower() == "swimming"]

    return swimming_data


def standardize_event_names(swimming_data: pd.DataFrame) -> pd.DataFrame:
    """Standardize the event names in the swimming data."""
    
    # make lowercase and remove whitespace
    swimming_data["Event"] = swimming_data["Event"].str.lower().str.strip()
    # replace metres with m
    swimming_data["Event"] = swimming_data["Event"].str.replace(" metres", "m")
    swimming_data["Event"] = swimming_data["Event"].str.replace("metres", "m")
    # remove swimming from the event name
    swimming_data["Event"] = swimming_data["Event"].str.replace("swimming ", "")
    swimming_data["Event"] = swimming_data["Event"].str.replace("swimming", "")
    # replace the multiplication symbol with x
    swimming_data["Event"] = swimming_data["Event"].str.replace("×", "x")
    # remove the space between 4 x 100m
    swimming_data["Event"] = swimming_data["Event"].str.replace("4 x 100","4x100")
    # remove the space between 4 x 200m
    swimming_data["Event"] = swimming_data["Event"].str.replace("4 x 200","4x200")
    # remove any commas
    swimming_data["Event"] = swimming_data["Event"].str.replace(",", "")    
    # remove any whitespace
    swimming_data["Event"] = swimming_data["Event"].str.strip()
    
    return swimming_data

def assign_gender(swimming_data: pd.DataFrame) -> pd.DataFrame:
    """Assign the gender category to the swimming data. 
    Extract the string of men or women or mixed from the event name and assign
    it to a new column called Category."""

    # check for men or women or mixed in the event name
    swimming_data["Category"] = swimming_data["Event"].str.extract(r"(men|women|mixed)")
    # remove women or women's or any variation of punctionation
    swimming_data["Event"] = swimming_data["Event"].str.replace(r"women(?:'s|`s)?", "")
        # remove mixed from event name
    swimming_data["Event"] = swimming_data["Event"].str.replace(r"mixed", "")
        # remove men or men's or any variation of punctionation
    swimming_data["Event"] = swimming_data["Event"].str.replace(r"men(?:'s|`s)?", "")
    # remove whitespace
    swimming_data["Event"] = swimming_data["Event"].str.strip()
    
    return swimming_data

###############################################
# TESTING
###############################################
def test_extract_swimming_data():
    swimming_data = extract_swimming_data(OLYMPICS_DATA_PATH)
    assert swimming_data.shape == (3258, 9)
    assert swimming_data["Sport"].str.lower().unique() == ["swimming"]
    assert swimming_data["Medal"].nunique() == 3
    assert swimming_data["Year"].nunique() == 31
    assert swimming_data["Season"].unique() == ["Summer"]

def test_standardize_event_names():
    swimming_data = extract_swimming_data(OLYMPICS_DATA_PATH)
    swimming_data = standardize_event_names(swimming_data)
    assert swimming_data["Event"].str.contains("swimming").sum() == 0
    assert swimming_data["Event"].str.contains("metres").sum() == 0
    assert swimming_data["Event"].str.contains("4 x 100").sum() == 0
    assert swimming_data["Event"].str.contains("4 x 200").sum() == 0
    assert swimming_data["Event"].str.contains("4 x 100 m").sum() == 0
    assert swimming_data["Event"].str.contains("4 x 200 m").sum() == 0
    assert swimming_data['Event'].str.contains("×").sum() == 0
    
def test_assign_gender():
    swimming_data = extract_swimming_data(OLYMPICS_DATA_PATH)
    swimming_data = standardize_event_names(swimming_data)
    swimming_data = assign_gender(swimming_data)
    assert swimming_data["Category"].nunique() == 3
