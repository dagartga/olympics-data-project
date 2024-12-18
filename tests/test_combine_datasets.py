import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pandas as pd
import olympics_data_project.data_cleaning.combine_datasets as cd
from olympics_data_project.data_cleaning.combine_datasets import (
    PARIS_PATH,
    TOKYO_PATH,
    KAGGLE_PATH,
    FINAL_COLUMNS,
)


def test_import_paris_data():
    paris_data = cd.import_paris_data(PARIS_PATH)
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
    tokyo_data = cd.import_tokyo_data(TOKYO_PATH)
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
    kaggle_data = cd.import_kaggle_data(KAGGLE_PATH)
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


def test_combine_datasets():
    paris_data = cd.import_paris_data(PARIS_PATH)
    tokyo_data = cd.import_tokyo_data(TOKYO_PATH)
    kaggle_data = cd.import_kaggle_data(KAGGLE_PATH)
    combined_data = cd.combine_datasets()
    # check the column number is correct
    assert combined_data.shape[1] == 9
    # ensure the combined rows equal the sum of the individual datasets
    assert (
        combined_data.shape[0]
        == paris_data.shape[0] + tokyo_data.shape[0] + kaggle_data.shape[0]
    )
    assert combined_data.columns.tolist() == FINAL_COLUMNS


def test_format_strings():
    data = pd.DataFrame(
        {
            "Athlete": ["Usain Bolt", "CALEB DRESSEL"],
            "Country": ["Jamaica", "United States"],
            "Season": ["Summer", "SUMMER"],
            "City": ["Rio", "PARIS"],
            "Year": [2016, 2024],
            "Sport": ["Athletics", "SWIMMING"],
            "Event": ["100m", "100m BUTTERFLY"],
            "Medal": ["Gold", "GOLD"],
        }
    )

    formatted_data = cd.format_the_strings(data)
    assert formatted_data["Athlete"].tolist() == ["Usain Bolt", "Caleb Dressel"]
    assert formatted_data["Country"].tolist() == ["Jamaica", "United States"]
    assert formatted_data["Season"].tolist() == ["Summer", "Summer"]
    assert formatted_data["City"].tolist() == ["Rio", "Paris"]
    assert formatted_data["Sport"].tolist() == ["Athletics", "Swimming"]
    assert formatted_data["Event"].tolist() == ["100M", "100M Butterfly"]
    assert formatted_data["Medal"].tolist() == ["Gold", "Gold"]