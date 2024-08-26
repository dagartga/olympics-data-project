import pandas as pd


TOKYO_PATH = "./data/processed/tokyo2020_results.csv"
PARIS_PATH = "./data/processed/paris2024_medal.csv"
KAGGLE_PATH = "./data/processed/kaggle1896_to_2016_results.csv"


def import_paris_data(paris_path: str) -> pd.DataFrame:
    """Import the Paris 2024 Olympics dataset from the specified path."""
    return pd.read_csv(paris_path)


def import_tokyo_data(tokyo_path: str) -> pd.DataFrame:
    """Import the Tokyo 2020 Olympics dataset from the specified path."""
    return pd.read_csv(tokyo_path)


def import_kaggle_data(kaggle_path: str) -> pd.DataFrame:
    """Import the Kaggle Olympics dataset from the specified path.
    This contains data from 1896 to 2016."""
    return pd.read_csv(kaggle_path)


###############################################
# TESTING
###############################################


def test_import_paris_data():
    paris_data = import_paris_data(PARIS_PATH)
    assert paris_data.shape == (139, 7)
    assert paris_data.columns.tolist() == [
        "Athlete/Team",
        "Country_Code",
        "Year",
        "Season",
        "Sport",
        "Event",
        "Medal",
    ]


def test_import_tokyo_data():
    tokyo_data = import_tokyo_data(TOKYO_PATH)
    assert tokyo_data.shape == (339, 7)
    assert tokyo_data.columns.tolist() == [
        "Athlete/Team",
        "Country_Code",
        "Year",
        "Season",
        "Sport",
        "Event",
        "Medal",
    ]
