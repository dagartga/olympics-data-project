### Data Check:
# According to ChatGPT there were 33 sports and 339 medaling events in Tokyo 2020.
# And 329 medaling events across 45 different sports in Paris 2024 and 206 countries in Paris.


import pandas as pd
import json
import regex as re


KAGGLE_OLYMPICS = "./data/raw/olympics_1896_2016_data.csv"
TOKYO_2020 = "./data/raw/tokyo2020_medals.json"
PARIS_2024 = "./data/raw/paris2024_medals.json"
NOC_PATH = "./data/raw/noc_regions.csv"

TOKYO_YEAR = "2020"
TOKYO_SEASON = "Summer"
TOKYO_CITY = "Tokyo"

FINAL_COLUMNS = ["Athlete", "NOC", "Year", "Season", "City", "Sport", "Event", "Medal"]
MEDALS = ["Gold", "Silver", "Bronze"]


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

    # create a list to hold each row as a list of values
    rows = []

    # iterate through the medals and athletes
    for medal, athlete, noc in zip(
        MEDALS, [gold, silver, bronze], [gold, silver, bronze]
    ):
        rows.append(
            [athlete, noc, TOKYO_YEAR, TOKYO_SEASON, TOKYO_CITY, sport, event, medal]
        )

    # create a DataFrame from the collected rows
    final_event_df = pd.DataFrame(rows, columns=FINAL_COLUMNS)

    return final_event_df


def split_medals(results: list) -> tuple:
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

    if country_indices == [0, 1, 2]:
        gold = [results[0]]
        silver = [results[1]]
        bronze = [results[2]]
    elif country_indices == [1, 3, 5]:
        gold = results[:2]
        silver = results[2:4]
        bronze = results[4:]
    # tie for gold indices
    elif country_indices == [2, 3, 5]:
        gold = results[:4]
        silver = []
        bronze = results[4:]
    # tie for silver indices
    elif country_indices == [1, 4, 5]:
        gold = results[:2]
        silver = results[2:]
        bronze = []
    # tie for bronze indices
    else:
        gold = results[:2]
        silver = results[2:4]
        bronze = results[4:]

    return gold, silver, bronze


def split_athelete_country(df):
    """Takes in a dataframe and splits the athlete and country into separate columns.

    Args:
        df (pd.DataFrame): A dataframe with the athlete and country in the same column.

    Returns:
        pd.DataFrame: A dataframe with the athlete and country in separate columns.
    """

    # create a new dataframe with the athlete and country split
    new_df = df.copy()
    for i, row in df.iterrows():
        # for team sports choose None for Athlete
        if len(row["Athlete"]) == 1:
            new_df.at[i, "Athlete"] = None
            new_df.at[i, "NOC"] = row["Athlete"][0]
        # fpr individual sports split the athlete and country
        elif len(row["Athlete"]) == 2:
            new_df.at[i, "Athlete"] = row["Athlete"][0]
            new_df.at[i, "NOC"] = row["Athlete"][1]

    return new_df


def remove_ties(df):
    """Takes in the tokyo 2020 dataframe and processes the medal ties
    by extracting the proper athlete and country values from the list object
    in the columns Athlete and NOC. The medal column is also updated with
    (Tie) to signify that there was a tie. For each tie, there is an individual
    row created for each athlete and country with duplicate medal values."""
    # get an index list of medal ties
    ties = [
        i
        for i, row in df.iterrows()
        if (row["Athlete"] == row["NOC"] and len(row["Athlete"]) > 0)
    ]
    # for each tie create a duplicate row with the second value values and reset the index
    for i in ties:
        athletes_and_countries = df.loc[i, "Athlete"]
        assert (
            len(athletes_and_countries) == 4
        ), f"Index {i}, There should be 4 values in the list"
        # create a temp dataframe from the tied results row
        temp_df = df.loc[i].copy()
        temp_df = temp_df.to_frame().T
        # make a duplicate row
        temp_df = pd.concat([temp_df, temp_df], ignore_index=True)
        # take the first athlete and country and put it in the first row
        temp_df.loc[0, "Athlete"] = athletes_and_countries[0]
        temp_df.loc[0, "NOC"] = athletes_and_countries[2]
        temp_df.loc[0, "Medal"] = temp_df.loc[0, "Medal"] + " (Tie)"
        # take the second athlete and country and put it in the second row
        temp_df.loc[1, "Athlete"] = athletes_and_countries[1]
        temp_df.loc[1, "NOC"] = athletes_and_countries[3]
        temp_df.loc[1, "Medal"] = temp_df.loc[1, "Medal"] + " (Tie)"
        # append the new rows
        df = pd.concat([df, temp_df], ignore_index=True)

    # remove the tied rows
    clean_ties_df = df.drop(ties)

    return clean_ties_df


def clean_noc_data(df: pd.DataFrame) -> pd.DataFrame:
    """Some NOC values are lists and should be strings."""
    df["NOC"] = df["NOC"].apply(lambda x: ",".join(x) if isinstance(x, list) else x)
    return df


def assign_country_to_tokyo(df: pd.DataFrame) -> pd.DataFrame:
    """Match the NOC with the Country name for the Tokyo 2020 dataframe."""

    # load the NOC data
    noc_df = pd.read_csv(NOC_PATH)

    # merge the dataframes
    final_df = pd.merge(df, noc_df[["NOC", "region"]], on="NOC", how="left")

    # rename columns
    final_df.rename(columns={"region": "Country"}, inplace=True)

    return final_df

def fill_na_athlete(df: pd.DataFrame) -> pd.DataFrame:
    """Fill the None values in the Athlete column with the Country value."""
    df["Athlete"] = df["Athlete"].fillna(df["Country"])
    return df


##################################################
# Testing
##################################################


def test_simple_split_medals():
    results = ["USA", "CAN", "GBR"]
    assert split_medals(results) == (["USA"], ["CAN"], ["GBR"])

    results = ["Michael Phelps", "USA", "Ryan Lochte", "USA", "Laszlo Cseh", "HUN"]
    assert split_medals(results) == (
        ["Michael Phelps", "USA"],
        ["Ryan Lochte", "USA"],
        ["Laszlo Cseh", "HUN"],
    )


def test_gold_tie():
    results = ["Michael Phelps", "Ryan Lochte", "USA", "USA", "Laszlo Cseh", "HUN"]
    assert split_medals(results) == (
        ["Michael Phelps", "Ryan Lochte", "USA", "USA"],
        [],
        ["Laszlo Cseh", "HUN"],
    )


def test_silver_tie():
    results = ["Michael Phelps", "USA", "Ryan Lochte", "Laszlo Cseh", "USA", "HUN"]
    assert split_medals(results) == (
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
    assert split_medals(results) == (
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

    final_df = create_event_df(test_df.iloc[0])
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
    clean_noc_df = clean_noc_data(df)
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

    country_df = assign_country_to_tokyo(df)

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
            "Event": ["4X100M Freestyle Relay", "4X100M Freestyle Relay", "4X100M Freestyle Relay"],
        }
    )

    filled_df = fill_na_athlete(df)

    assert filled_df["Athlete"].isna().sum() == 0
    assert filled_df["Athlete"].values[0] == "United States"
    assert filled_df["Athlete"].values[1] == "Italy"
    assert filled_df["Athlete"].values[2] == "Australia"

if __name__ == "__main__":

    # Load the json file
    with open(TOKYO_2020) as f:
        data_tokyo = json.load(f)

    sports_ls = list()
    events_lS = list()
    medals_ls = list()

    # iterate through the keys (Sport) and results
    for key, val in data_tokyo.items():
        sport = key
        for event, results in val.items():
            sports_ls.append(sport)
            events_lS.append(event)
            medals_ls.append(results)

    # create a dataframe
    tokyo_df = pd.DataFrame(
        {"Sport": sports_ls, "Event": events_lS, "Results": medals_ls}
    )

    expanded_tokyo_df = pd.DataFrame(columns=FINAL_COLUMNS)

    # iterate through the rows and extract the team, noc and medal
    # from the results column and add them to the final dataframe
    for i, row in tokyo_df.iterrows():
        temp_df = create_event_df(row)
        expanded_tokyo_df = pd.concat([expanded_tokyo_df, temp_df], ignore_index=True)

    # split the athlete and country values into the correct columns
    final_tokyo_df = split_athelete_country(expanded_tokyo_df)

    # process the ties
    cleaned_final_tokyo_df = remove_ties(final_tokyo_df)

    # clean noc data to remove any lists
    cleaned_final_tokyo_df = clean_noc_data(cleaned_final_tokyo_df)

    # assign the country to the NOC
    cleaned_final_tokyo_df = assign_country_to_tokyo(cleaned_final_tokyo_df)

    # fill the None values in the Athlete column for tokyo
    cleaned_final_tokyo_df = fill_na_athlete(cleaned_final_tokyo_df)

    # save the final dataframe
    cleaned_final_tokyo_df.to_csv("./data/processed/tokyo2020_results.csv", index=False)
