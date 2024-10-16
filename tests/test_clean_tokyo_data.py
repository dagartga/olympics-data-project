import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pandas as pd
import olympics_data_cleaning.clean_tokyo_data as ctd


def test_simple_split_medals():
    results = ["USA", "CAN", "GBR"]
    assert ctd.split_medals(results) == (["USA"], ["CAN"], ["GBR"])

    results = ["Michael Phelps", "USA", "Ryan Lochte", "USA", "Laszlo Cseh", "HUN"]
    assert ctd.split_medals(results) == (
        ["Michael Phelps", "USA"],
        ["Ryan Lochte", "USA"],
        ["Laszlo Cseh", "HUN"],
    )


def test_gold_tie():
    results = ["Michael Phelps", "Ryan Lochte", "USA", "USA", "Laszlo Cseh", "HUN"]
    assert ctd.split_medals(results) == (
        ["Michael Phelps", "Ryan Lochte", "USA", "USA"],
        [],
        ["Laszlo Cseh", "HUN"],
    )


def test_silver_tie():
    results = ["Michael Phelps", "USA", "Ryan Lochte", "Laszlo Cseh", "USA", "HUN"]
    assert ctd.split_medals(results) == (
        ["Michael Phelps", "USA"],
        ["Ryan Lochte", "Laszlo Cseh", "USA", "HUN"],
        [],
    )


def test_bronze_tie():
    results = [
        "Michael Phelps",
        "USA",
        "Ryan Lochte",
        "USA",
        "Laszlo Cseh",
        "Chad Le Clos",
        "HUN",
        "RSA",
    ]
    assert ctd.split_medals(results) == (
        ["Michael Phelps", "USA"],
        ["Ryan Lochte", "USA"],
        ["Laszlo Cseh", "Chad Le Clos", "HUN", "RSA"],
    )


def test_event_df():
    test_df = pd.DataFrame(
        {
            "Sport": "Swimming",
            "Event": "100M Freestyle (Men)",
            "Results": [
                [
                    "Caeleb Dressel",
                    "USA",
                    "Kyle Chalmers",
                    "AUS",
                    "Kliment Kolesnikov",
                    "ROC",
                ]
            ],
        }
    )

    final_df = ctd.create_event_df(test_df.iloc[0])
    assert final_df.shape == (3, 8)
    assert final_df["Sport"].unique()[0] == "Swimming"
    assert final_df[final_df["Medal"] == "Gold"]["Athlete"].values[0] == [
        "Caeleb Dressel",
        "USA",
    ]
    assert final_df[final_df["Medal"] == "Silver"]["Athlete"].values[0] == [
        "Kyle Chalmers",
        "AUS",
    ]
    assert final_df[final_df["Medal"] == "Bronze"]["Athlete"].values[0] == [
        "Kliment Kolesnikov",
        "ROC",
    ]


def test_clean_noc_data():
    df = pd.DataFrame({"NOC": [["USA"], ["CAN"], ["GBR"], "FRA"]})
    clean_noc_df = ctd.clean_noc_data(df)
    assert clean_noc_df["NOC"].values[0] == "USA"
    assert clean_noc_df["NOC"].values[1] == "CAN"
    assert clean_noc_df["NOC"].values[2] == "GBR"
    assert clean_noc_df["NOC"].values[3] == "FRA"


def test_assign_country_to_tokyo():
    df = pd.DataFrame(
        {
            "Athlete": ["Caeleb Dressel", "Kyle Chalmers", "Kliment Kolesnikov"],
            "NOC": ["USA", "AUS", "ROC"],
            "Year": [2020, 2020, 2020],
            "Season": ["Summer", "Summer", "Summer"],
            "City": ["Tokyo", "Tokyo", "Tokyo"],
            "Sport": ["Swimming", "Swimming", "Swimming"],
            "Event": ["100M Freestyle", "100M Freestyle", "100M Freestyle"],
        }
    )

    country_df = ctd.assign_country_to_tokyo(df)

    assert "Country" in country_df.columns
    assert country_df["Country"].isna().sum() == 0
    assert country_df["Country"].values[0] == "United States"
    assert country_df["Country"].values[1] == "Australia"
    assert country_df["Country"].values[2] == "Russia"


def test_fill_na_athlete():
    df = pd.DataFrame(
        {
            "Athlete": [None, None, None],
            "NOC": ["USA", "ITA", "AUS"],
            "Country": ["United States", "Italy", "Australia"],
            "Year": [2020, 2020, 2020],
            "Season": ["Summer", "Summer", "Summer"],
            "City": ["Tokyo", "Tokyo", "Tokyo"],
            "Sport": ["Swimming", "Swimming", "Swimming"],
            "Event": [
                "4X100M Freestyle Relay",
                "4X100M Freestyle Relay",
                "4X100M Freestyle Relay",
            ],
        }
    )

    filled_df = ctd.fill_na_athlete(df)

    assert filled_df["Athlete"].isna().sum() == 0
    assert filled_df["Athlete"].values[0] == "United States"
    assert filled_df["Athlete"].values[1] == "Italy"
    assert filled_df["Athlete"].values[2] == "Australia"
