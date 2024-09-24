# take the json file and convert it to a csv file
# data scraped from https://apnews.com/article/olympics-2024-medal-winners-today-b9522fd1223ae6599569ffe1ee48cc62

import json
import pandas as pd
import regex as re

PARIS_PATH = "../data/raw/paris2024_results.json"
COUNTRY_PATH = "../data/raw/country_codes.csv"
SPORTS_PATH = "../data/raw/sports_list.json"


def clean_paris_data(path):
    """Clean the json data and save it to a csv file"""
    data = load_data(path)

    # remove dates from h2 data
    h2_data = remove_dates_from_h2(data["h2"])
    # remove symbols from h2 data
    h2_data = remove_symbols_from_h2(h2_data)
    # combine the CYCLING and TEAM PURSUIT data
    h2_data = combine_cycling_pursuit(h2_data)
    # update the 3X3 BASKETBALL data
    h2_data = update_3x3_basketball(h2_data)
    # clean the SWIMMING RELAYS data
    h2_data = clean_swimming_relays(h2_data)

    # remove headlines from p data
    p_data = remove_headlines_from_p(data["p"])
    # clean medals events from p data
    p_data = clean_medals_events_from_p(p_data)

    data = {"h2": h2_data, "p": p_data}

    # group the medals with the events
    grouped_medals = group_medals(data)
    # combine the grouped medals with the h2 data
    combined_data = combine_grouped_medals_with_h2(h2_data, grouped_medals)

    # geat the events from the p data
    p_events = get_p_events(p_data)

    # store the p events in a json file
    save_p_events(p_events)

    # convert the cleaned data to a DataFrame
    df = convert_to_df(combined_data)

    # adjust the event and sports
    df = adjust_event_and_sports(df)

    # replace the sport names
    df = replace_sport(df)

    # insert the p events into the DataFrame
    df = insert_p_events(df, p_events)

    # convert the medal list to a DataFrame
    df = convert_medal_list_to_df(df)

    # remove the medal colors
    df = remove_medal_colors(df)

    # melt the medal data
    df = melt_medals(df)

    # split country and athlete
    df = split_country_athlete(df, COUNTRY_PATH)

    # deal with some events that tie for bronze
    bronze_df, tie_list = deal_with_ties(df)
    df = remove_bronze_ties(df, bronze_df, tie_list)

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
        if val == "CYCLING" and "TEAM PURSUIT" in h2_data[i + 1]:
            continue

        elif "TEAM PURSUIT" in val:
            updated_h2_data.append(f"CYCLING {val}")

        else:
            updated_h2_data.append(val)

    return updated_h2_data


def update_3x3_basketball(h2_data: list) -> list:
    """The Women's 3X3 Basketball simply says WOMEN,
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
        if val == "SWIMMING" and "1500M" in h2_data[i + 1]:
            updated_h2_data.append("WOMEN’S 50M FREESTYLE")
            updated_h2_data.append("WOMEN’S 4x100M MEDLEY RELAY")
        elif val == "MEN’S 1500M FREESTYLE":
            updated_h2_data.append(val)
            updated_h2_data.append("MEN’S 4x100M MEDLEY RELAY")
        else:
            updated_h2_data.append(val)

    return updated_h2_data


def remove_headlines_from_p(p_data: list) -> list:
    """Remove any string values that are not events or results.
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
        elif (
            val.lower().startswith("gold:")
            or val.lower().startswith("silver:")
            or val.lower().startswith("bronze:")
        ):
            results_data.append(val)
        # remove any events that slipped through the first check
        elif val.lower().startswith("men") or val.lower().startswith("women"):
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
    medals = re.compile(r"(?<!^)(Gold:|GOLD:|Silver:|Bronze:)")

    for val in p_data:
        # check if the value matches the regex pattern
        if medals.search(val):
            if "Gold:" in val:
                event, medal = val.split("Gold:")
                medal = "Gold:" + medal
                event_results.append(event.rstrip())
                event_results.append(medal)
            elif "GOLD:" in val:
                event, medal = val.split("GOLD:")
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
    no_medals = re.compile(r"^(?!Gold:|Silver:|Bronze:|GOLD:)")
    # iterate through the p data
    for val in p_data:
        # check if the value matches the regex pattern
        if no_medals.match(val) and val != "SYNCHRONIZED 10-METER PLATFORM":
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

    h2_data.pop(251)
    h2_data.pop(254)
    h2_data.insert(256, "MEN’S 90KG")
    h2_data.insert(276, "MEN’S 4X200M FREESTYLE RELAY")
    h2_data.insert(172, "SWIMMING")
    h2_data.pop(173)
    h2_data.pop(251)
    h2_data.insert(251, "CYCLING")

    combined_data = [[x, y] for x, y in zip(h2_data, grouped_medals)]

    return combined_data


def convert_to_df(cleaned_data: list) -> pd.DataFrame:
    """Convert the cleaned data to a pandas DataFrame"""
    df = pd.DataFrame(cleaned_data, columns=["Sport", "Medal Winners"])

    # create a duplicate colum of Sport named Event
    df["Event"] = df["Sport"]

    return df


def open_sports_list(path: str) -> list:
    """Open the sports list from a json file"""
    with open(path) as f:
        sports = json.load(f)
    return sports


def adjust_event_and_sports(df: pd.DataFrame) -> pd.DataFrame:
    SPORT_LIST = open_sports_list(SPORTS_PATH)
    j = 0
    for i, row in df.iterrows():
        try:
            if j >= len(SPORT_LIST):
                df.loc[i, "Sport"] = SPORT_LIST[-1]
            elif row["Sport"] == SPORT_LIST[j]:
                j += 1
            else:
                df.loc[i, "Sport"] = SPORT_LIST[j - 1]
        except:
            continue
    return df


def replace_sport(df: pd.DataFrame) -> pd.DataFrame:
    df["Sport"] = df["Sport"].replace(
        {
            "CYCLING MEN’S TEAM PURSUIT": "CYCLING",
            "CYCLING WOMEN’S TEAM PURSUIT": "CYCLING",
            "MEN’S 3X3 BASKETBALL": "3X3 BASKETBALL",
            "WOMEN’S 3X3 BASKETBALL": "3X3 BASKETBALL",
        }
    )
    return df


def save_p_events(p_events: list):
    """Save the p events to a json file"""
    file_path = "../data/raw/p_events.json"

    with open(file_path, "w") as file:

        json.dump(p_events, file)

    print(f"File saved to {file_path}")


def insert_p_events(df: pd.DataFrame, p_events: list) -> pd.DataFrame:
    temp_events = p_events.copy()
    temp_df = df.copy()

    # remove index 72 from temp_events
    temp_events.pop(72)

    # remove index 132 from temp_events
    temp_events.pop(132)

    # remove index 134 from temp_events
    temp_events.pop(134)

    # remove WOMEN'S 4X100M MEDLEY RELAY
    temp_events.remove("WOMEN’S 4x100M MEDLEY RELAY")
    # remove MEN'S 4X100M MEDLEY RELAY
    temp_events.remove("MEN’S 4x100M MEDLEY RELAY")

    j = 0
    for i, row in temp_df.iterrows():
        if i == 28:
            temp_df.loc[i, "Event"] = "MEN’S"
        if i == 60:
            temp_df.loc[i, "Event"] = "WOMEN’S"
        if i == 103:
            temp_df.loc[i, "Event"] = "WOMEN’S KITE"
        if i == 114:
            temp_df.loc[i, "Event"] = "MEN’S DINGHY"
            j += 2
        if i == 251:
            temp_df.loc[i, "Event"] = "WOMEN’S PARK"
        if i == 253:
            temp_df.loc[i, "Event"] = "WOMEN’S SYNCHRONIZED 10-METER PLATFORM"
        if i == 314:
            temp_df.loc[i, "Event"] = "MEN’S"
        if row["Sport"] == row["Event"]:
            try:
                temp_df.loc[i, "Event"] = temp_events[j]
                j += 1
            except:
                print(i)
    return temp_df


def convert_medal_list_to_df(df: pd.DataFrame) -> pd.DataFrame:
    """Take the results from column Medal Winners and split them into
    separate columns for Gold, Silver, and Bronze.
    Put Medal Winners results in the Tie column if there is a tie"""

    # create copy of the DataFrame
    temp_df = df.copy()

    # create new columns for Gold, Silver, and Bronze
    temp_df["Gold"] = None
    temp_df["Silver"] = None
    temp_df["Bronze"] = None
    temp_df["Tie"] = None

    # iterate through the DataFrame
    for i, row in temp_df.iterrows():

        # iterate through the medals
        for medal in row["Medal Winners"]:
            # check if the medal is Gold
            if "Gold" in medal:
                # check the count of Gold medals
                count = temp_df.loc[i, "Medal Winners"].count("Gold")
                # check if there is a tie
                if count > 1:
                    temp_df.loc[i, "Tie"] = row["Medal Winners"]
                temp_df.loc[i, "Gold"] = medal
            # check if the medal is Silver
            elif "Silver" in medal:
                # check the count of Silver medals
                count = temp_df.loc[i, "Medal Winners"].count("Silver")
                # check if there is a tie
                if count > 1:
                    temp_df.loc[i, "Tie"] = row["Medal Winners"]
                temp_df.loc[i, "Silver"] = medal
            # check if the medal is Bronze
            elif "Bronze" in medal:
                # check the count of Bronze medals
                count = temp_df.loc[i, "Medal Winners"].count("Bronze")
                # check if there is a tie
                if count > 1:
                    temp_df.loc[i, "Tie"] = row["Medal Winners"]
                temp_df.loc[i, "Bronze"] = medal

    return temp_df


def remove_medal_colors(df: pd.DataFrame) -> pd.DataFrame:
    """For each value in the Gold, Silver, and Bronze columns,
    remove the color from the string"""

    # create copy of the DataFrame
    temp_df = df.copy()

    # remove the color from the Gold column
    temp_df["Gold"] = temp_df["Gold"].str.replace("Gold: ", "")
    # remove the color from the Silver column
    temp_df["Silver"] = temp_df["Silver"].str.replace("Silver: ", "")
    # remove the color from the Bronze column
    temp_df["Bronze"] = temp_df["Bronze"].str.replace("Bronze: ", "")

    return temp_df


def melt_medals(df: pd.DataFrame) -> pd.DataFrame:
    """Create a melted table of the Gold, Silver, and Bronze medals
    to list medal color and the athlete for each event

    The new columns will be Sport, Event, Medal, and Athlete.
    Where each medal color is listed in Medal along wtih the athlete name"""

    # create a copy of the DataFrame
    temp_df = df.copy()

    # melt the DataFrame
    melted_df = temp_df.melt(
        id_vars=["Sport", "Event"],
        value_vars=["Gold", "Silver", "Bronze"],
        var_name="Medal",
        value_name="Athlete",
    )

    return melted_df


def split_country_athlete(df: pd.DataFrame, path: str) -> pd.DataFrame:
    """The Athlete column has the athlete name and country.
    Check the country name against the list of countries and split the
    athlete name and country into separate columns"""

    # create a copy of the DataFrame
    temp_df = df.copy()
    other_temp_df = df.copy()

    # load the list of countries from csv
    countries = pd.read_csv(path)
    country = countries["country_name"].tolist()

    # create a new column for the country
    temp_df["Country"] = None

    # iterate through the DataFrame
    for i, row in other_temp_df.iterrows():
        if row["Athlete"] is None:
            continue
        elif "," in row["Athlete"]:
            # split Athlete column on the comma
            athlete = row["Athlete"].split(", ")
            # check if the country is in the list of countries
            if athlete[1].strip() in country:
                temp_df.loc[i, "Country"] = athlete[1].strip()
                temp_df.loc[i, "Athlete"] = athlete[0]
            elif athlete[1].strip() == "Britain":
                temp_df.loc[i, "Country"] = "Great Britain"
                temp_df.loc[i, "Athlete"] = athlete[0]
            elif athlete[1].strip() == "AIN":
                temp_df.loc[i, "Country"] = "Belarus"
                temp_df.loc[i, "Athlete"] = athlete[0]
            elif athlete[0].strip() == "Yang":
                temp_df.loc[i, "Country"] = "China"
                temp_df.loc[i, "Athlete"] = "Yang Liu"
            # if the athlete[1] ends with period remove it
            elif athlete[1].strip().endswith("."):
                country_updated = athlete[1][:-1]
                if country_updated in country:
                    temp_df.loc[i, "Country"] = country_updated
                    temp_df.loc[i, "Athlete"] = athlete[0]
        elif " (" in row["Athlete"]:
            # split Athlete column on the (
            athlete = row["Athlete"].split(" (")
            # check if the country is in the list of countries
            if athlete[0].strip() in country:
                temp_df.loc[i, "Country"] = athlete[0].strip()
                temp_df.loc[i, "Athlete"] = athlete[1].strip().replace(")", "")
        else:
            temp_df.loc[i, "Country"] = row["Athlete"]

    # do a second pass to deal with multiple athletes
    for i, row in temp_df[temp_df["Country"].isna()].iterrows():
        if row["Athlete"] is None:
            continue
        elif "," and " (" in row["Athlete"]:
            # split Athlete column on the comma
            athlete = row["Athlete"].split(" (")
            # check if the country is in the list of countries
            if athlete[0].strip() in country:
                temp_df.loc[i, "Country"] = athlete[0].strip()
                temp_df.loc[i, "Athlete"] = athlete[1]
            elif athlete[0].strip() == "Britain":
                temp_df.loc[i, "Country"] = "Great Britain"
                temp_df.loc[i, "Athlete"] = athlete[1]

    return temp_df


def deal_with_ties(df: pd.DataFrame) -> pd.DataFrame:
    """Events with multiple Bronze medals are Judo, Wrestling, Taekwondo and Boxing"""
    temp_df = df[df["Country"].isna()].copy()

    # list to store the bronze results
    bronze_list = []

    # create a list of indices with ties
    tie_list = []

    # create a list of the sports with ties
    sports_with_ties = ["WRESTLING", "JUDO", "TAEKWONDO", "BOXING"]
    for i, row in temp_df.iterrows():
        if (
            row["Sport"] in sports_with_ties
            and "Bronze" in row["Medal"]
            and "and" in row["Athlete"]
        ):
            # split the athlete column on the word 'and'
            athletes = row["Athlete"].split(" and ")
            # create a new row for each athlete
            try:
                for athlete in athletes:
                    if "Dauren Kurugliev" in athlete:
                        athlete_name = "Dauren Kurugliev"
                        athlete_country = "Greece"

                    else:
                        athlete_split = athlete.split(", ")
                        athlete_name = athlete_split[0]
                        athlete_country = athlete_split[1]
                    bronze_list.append(
                        {
                            "Sport": row["Sport"],
                            "Event": row["Event"],
                            "Medal": row["Medal"],
                            "Athlete": athlete_name,
                            "Country": athlete_country,
                        }
                    )
                    tie_list.append(i)
            except:
                continue

    # create a DataFrame from the list of bronze results
    bronze_df = pd.DataFrame(bronze_list)

    return bronze_df, tie_list


def remove_bronze_ties(
    df: pd.DataFrame, bronze_df: pd.DataFrame, tie_list: list
) -> pd.DataFrame:
    """Remove the rows with bronze ties and append the bronze_df to the original df"""

    temp_df = df.copy()
    temp_df = temp_df.drop(tie_list)
    temp_df = temp_df.append(bronze_df, ignore_index=True)

    return temp_df


############################################
# TESTING
############################################


def test_load_data():
    data = load_data(PARIS_PATH)
    assert type(data) == dict
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
    no_date = remove_dates_from_h2(test_data)
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
    no_symbol = remove_symbols_from_h2(test_data)
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
    no_headlines = remove_headlines_from_p(test_data)
    assert no_headlines == ["GOLD: Tom Pidcock, Britain", "WOMEN’S 500M SINGLE KAYAK"]


def test_clean_medals_events():
    test_data = ["MEN’S 90KG Gold: Lasha Bekauri, Georgia"]
    cleaned_data = clean_medals_events_from_p(test_data)
    assert cleaned_data == ["MEN’S 90KG", "Gold: Lasha Bekauri, Georgia"]


def test_update_3x3_basketball():
    test_data = [
        "MEN’S GRECO-ROMAN 60KG",
        "WOMEN’S FREESTYLE 68KG",
        "3X3 BASKETBALL",
        "WOMEN",
        "BADMINTON",
    ]
    updated_data = update_3x3_basketball(test_data)
    assert updated_data == [
        "MEN’S GRECO-ROMAN 60KG",
        "WOMEN’S FREESTYLE 68KG",
        "MEN’S 3X3 BASKETBALL",
        "WOMEN’S 3X3 BASKETBALL",
        "BADMINTON",
    ]


def test_clean_swimming_relays():
    test_data = ["SWIMMING", "MEN’S 1500M FREESTYLE"]
    cleaned_data = clean_swimming_relays(test_data)
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
    events = get_p_events(test_data)
    assert events == [
        "WOMEN’S MARATHON",
        "WOMEN’S",
        "MEN’S KEIRIN",
        "WOMEN’S 3X3 BASKETBALL Gold: United States",
    ]
