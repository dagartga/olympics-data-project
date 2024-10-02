import pandas as pd


TOKYO_PATH = "../data/processed/tokyo2020_results.csv"
PARIS_PATH = "../data/processed/paris2024_results.csv"
KAGGLE_PATH = "../data/processed/kaggle1896_to_2016_results.csv"

FINAL_COLUMNS = [
    "Athlete",
    "Country",
    "NOC",
    "Season",
    "Year",
    "City",
    "Sport",
    "Event",
    "Medal",
]


def combine_datasets() -> pd.DataFrame:
    """Concatenate the three datasets into one."""
    tokyo_df = import_tokyo_data(TOKYO_PATH)
    paris_df = import_paris_data(PARIS_PATH)
    kaggle_df = import_kaggle_data(KAGGLE_PATH)

    # order the columns to match the final columns
    tokyo_df = tokyo_df[FINAL_COLUMNS]
    paris_df = paris_df[FINAL_COLUMNS]
    kaggle_df = kaggle_df[FINAL_COLUMNS]

    # concatenate the dataframes
    return pd.concat([tokyo_df, paris_df, kaggle_df], ignore_index=True)


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
    assert paris_data.shape == (994, 9)
    assert paris_data.columns.tolist() == [
        "Sport",
        "Event",
        "Medal",
        "Athlete",
        "Country",
        "Year",
        "City",
        "Season",
        "NOC",
    ]


def test_import_tokyo_data():
    tokyo_data = import_tokyo_data(TOKYO_PATH)
    assert tokyo_data.shape == (1080, 9)
    assert tokyo_data.columns.tolist() == [
        "Athlete",
        "NOC",
        "Year",
        "Season",
        "City",
        "Sport",
        "Event",
        "Medal",
        "Country",
    ]


def test_import_kaggle_data():
    kaggle_data = import_kaggle_data(KAGGLE_PATH)
    assert kaggle_data.shape == (34088, 9)
    assert kaggle_data.columns.tolist() == [
        "Athlete",
        "Country",
        "NOC",
        "Season",
        "Year",
        "City",
        "Sport",
        "Event",
        "Medal",
    ]


def test_concatenate_datasets():
    paris_data = import_paris_data(PARIS_PATH)
    tokyo_data = import_tokyo_data(TOKYO_PATH)
    kaggle_data = import_kaggle_data(KAGGLE_PATH)
    combined_data = concatenate_datasets(tokyo_data, paris_data, kaggle_data)
    assert combined_data.shape[1] == 9
    assert (
        combined_data.shape[0]
        == paris_data.shape[0] + tokyo_data.shape[0] + kaggle_data.shape[0]
    )
    assert combined_data.columns.tolist() == FINAL_COLUMNS
