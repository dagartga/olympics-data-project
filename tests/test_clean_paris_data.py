import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pandas as pd
import olympics_data_cleaning.clean_paris_data as cpd
from olympics_data_cleaning.clean_paris_data import (
    PARIS_PATH,
    COUNTRY_PATH,
    SPORTS_PATH,
    CSV_SAVE_PATH,
    NOC_PATH,
)


def test_load_data():
    data = cpd.load_data(PARIS_PATH)
    assert isinstance(data, dict)
    assert data.keys() == {"h2", "p"}


def test_remove_dates_from_h2():
    test_data = [
        "Saturday, Aug. 10",
        "Sunday, Aug. 11",
        "Monday, Aug.12",
        "BOXING",
        "Tuesday, Aug. 13",
        "Wednesday, Aug. 14",
        "Thursday, Aug. 15",
        "Friday, Aug. 16",
    ]
    no_date = cpd.remove_dates_from_h2(test_data)
    assert no_date == ["BOXING"]


def test_remove_symbols_from_h2():
    test_data = [
        "CYCLING",
        "3X3 BASKETBALL",
        "ATHLETICS",
        "_______",
        "BOXING",
        "######",
    ]
    no_symbol = cpd.remove_symbols_from_h2(test_data)
    assert no_symbol == ["CYCLING", "3X3 BASKETBALL", "ATHLETICS", "BOXING"]


def test_remove_headlines_from_p():
    test_data = [
        "PARIS (AP) — The 2024 Olympics are done. The United States led the final medal standings with 126 total medals, ahead of China (91), Britain (65) and France (64). Below is a list of all the medal winners, day by day.",
        "\n",
        "2024 Paris Olympics:",
        "▶ See other events still in progress",
        "GOLD: Tom Pidcock, Britain",
        "WOMEN’S 500M SINGLE KAYAK",
    ]
    no_headlines = cpd.remove_headlines_from_p(test_data)
    assert no_headlines == ["GOLD: Tom Pidcock, Britain", "WOMEN’S 500M SINGLE KAYAK"]


def test_clean_medals_events():
    test_data = ["MEN’S 90KG Gold: Lasha Bekauri, Georgia"]
    cleaned_data = cpd.clean_medals_events_from_p(test_data)
    assert cleaned_data == ["MEN’S 90KG", "Gold: Lasha Bekauri, Georgia"]


def test_update_3x3_basketball():
    test_data = [
        "MEN’S GRECO-ROMAN 60KG",
        "WOMEN’S FREESTYLE 68KG",
        "3X3 BASKETBALL",
        "WOMEN",
        "BADMINTON",
    ]
    updated_data = cpd.update_3x3_basketball(test_data)
    assert updated_data == [
        "MEN’S GRECO-ROMAN 60KG",
        "WOMEN’S FREESTYLE 68KG",
        "MEN’S 3X3 BASKETBALL",
        "WOMEN’S 3X3 BASKETBALL",
        "BADMINTON",
    ]


def test_clean_swimming_relays():
    test_data = ["SWIMMING", "MEN’S 1500M FREESTYLE"]
    cleaned_data = cpd.clean_swimming_relays(test_data)
    assert cleaned_data == [
        "WOMEN’S 50M FREESTYLE",
        "WOMEN’S 4x100M MEDLEY RELAY",
        "MEN’S 1500M FREESTYLE",
        "MEN’S 4x100M MEDLEY RELAY",
    ]


def test_get_p_events():
    test_data = [
        "WOMEN’S MARATHON",
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
    events = cpd.get_p_events(test_data)
    assert events == [
        "WOMEN’S MARATHON",
        "WOMEN’S",
        "MEN’S KEIRIN",
        "WOMEN’S 3X3 BASKETBALL Gold: United States",
    ]


def test_group_medals():
    """Test that the group_medals function returns the
    medals and athlete data in a list of lists"""

    test_data = {
        "h2": ["TRACK AND FIELD", "BASKETBALL", "CYCLING"],
        "p": [
            "WOMEN’S MARATHON",
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
        ],
    }

    medals = cpd.group_medals(test_data)
    assert medals == [
        [
            "Gold: Netherlands (Sifan Hassan)",
            "Silver: Ethiopia (Tigst Assefa)",
            "Bronze: Kenya (Hellen Obiri)",
        ],
        ["Gold: United States", "Silver: France", "Bronze: Australia"],
        [
            "Gold: Netherlands (Harrie Lavreysen)",
            "Silver: Australia (Matthew Richardson)",
            "Bronze: Australia (Matthew Glaetzer",
        ],
    ]


def test_combine_group_medals_with_h2():
    """Test that the combine_grouped_medals_with_h2 function
    combines the Sport with the medal results"""

    h2_data = ["TRACK AND FIELD", "BASKETBALL", "CYCLING"]

    grouped_medals = [
        [
            "Gold: Netherlands (Sifan Hassan)",
            "Silver: Ethiopia (Tigst Assefa)",
            "Bronze: Kenya (Hellen Obiri)",
        ],
        ["Gold: United States", "Silver: France", "Bronze: Australia"],
        [
            "Gold: Netherlands (Harrie Lavreysen)",
            "Silver: Australia (Matthew Richardson)",
            "Bronze: Australia (Matthew Glaetzer",
        ],
    ]

    combined_data = cpd.combine_grouped_medals_with_h2(h2_data, grouped_medals)
    assert combined_data == [
        [
            "TRACK AND FIELD",
            [
                "Gold: Netherlands (Sifan Hassan)",
                "Silver: Ethiopia (Tigst Assefa)",
                "Bronze: Kenya (Hellen Obiri)",
            ],
        ],
        ["BASKETBALL", ["Gold: United States", "Silver: France", "Bronze: Australia"]],
        [
            "CYCLING",
            [
                "Gold: Netherlands (Harrie Lavreysen)",
                "Silver: Australia (Matthew Richardson)",
                "Bronze: Australia (Matthew Glaetzer",
            ],
        ],
    ]


def test_convert_to_df():
    """Test that the convert_to_df function returns a DataFrame"""

    test_data = [
        [
            "TRACK AND FIELD",
            [
                "Gold: Netherlands (Sifan Hassan)",
                "Silver: Ethiopia (Tigst Assefa)",
                "Bronze: Kenya (Hellen Obiri)",
            ],
        ],
        ["BASKETBALL", ["Gold: United States", "Silver: France", "Bronze: Australia"]],
        [
            "CYCLING",
            [
                "Gold: Netherlands (Harrie Lavreysen)",
                "Silver: Australia (Matthew Richardson)",
                "Bronze: Australia (Matthew Glaetzer",
            ],
        ],
    ]

    df = cpd.convert_to_df(test_data)
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (3, 3)
    assert df.columns.tolist() == ["Sport", "Medal Winners", "Event"]
