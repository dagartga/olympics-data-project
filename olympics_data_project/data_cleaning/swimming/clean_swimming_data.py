from pathlib import Path

import pandas as pd

# Get the current script's directory
base_dir = Path(__file__).parent
# convert the path to the project directory
project_dir = base_dir.parent.parent

# Construct the path to the all olympics data csv file
OLYMPICS_DATA_PATH = project_dir / "data" / "processed" / "all_olympics_data.csv"
# Construct the path to store the cleaned swimming data
SWIMMING_DATA_PATH = (
    project_dir / "data" / "processed" / "swimming" / "swimming_results.csv"
)


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
    swimming_data["Event"] = swimming_data["Event"].str.replace("4 x 100", "4x100")
    # remove the space between 4 x 200m
    swimming_data["Event"] = swimming_data["Event"].str.replace("4 x 200", "4x200")
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
    # capitalize the first letter
    swimming_data["Category"] = swimming_data["Category"].str.capitalize()
    # remove whitespace
    swimming_data["Event"] = swimming_data["Event"].str.strip()

    return swimming_data


def remove_gender_from_event(swimming_data: pd.DataFrame) -> pd.DataFrame:
    """Remove Men, Women, or Mixed from the event name in the swimming data."""

    # replace the word women
    swimming_data["Event"] = swimming_data["Event"].str.replace("women", "")
    # replace the word mixed
    swimming_data["Event"] = swimming_data["Event"].str.replace("mixed", "")
    # replace the word men
    swimming_data["Event"] = swimming_data["Event"].str.replace("men", "")

    return swimming_data


def remove_apostrophes(swimming_data: pd.DataFrame) -> pd.DataFrame:
    """Remove apostrophes from the event names in the swimming data."""

    swimming_data["Event"] = swimming_data["Event"].str.replace("'s ", "")
    swimming_data["Event"] = swimming_data["Event"].str.replace("’s ", "")
    swimming_data["Event"] = swimming_data["Event"].str.replace("s ", "")

    return swimming_data


def add_meters_to_event_name(swimming_data: pd.DataFrame) -> pd.DataFrame:
    """Add meters (m) to the event name if it is missing in the swimming data."""

    # create regex pattern to match 0 followed by sapce
    pattern = r"0\s"
    # check if the event name has 0 followed by space
    mask = swimming_data["Event"].str.contains(pattern)
    # replace 0 followed by space with 0m
    swimming_data.loc[mask, "Event"] = swimming_data.loc[mask, "Event"].str.replace(
        "0 ", "0m "
    )

    return swimming_data


def rename_10km_event(swimming_data: pd.DataFrame) -> pd.DataFrame:
    """Rename the 10 kilom event to 10km open water in the swimming data."""

    # rename the 10km event to 10k marathon
    swimming_data["Event"] = swimming_data["Event"].str.replace(
        "10m kilom open water", "10km open water"
    )

    return swimming_data


def replace_meters_with_yards(swimming_data: pd.DataFrame) -> pd.DataFrame:
    """If the event name has yard in it, replace the m with yds in the swimming data."""

    # create a mask to check if yard in the event name
    mask = swimming_data["Event"].str.contains("yard")
    # replace m with yds
    swimming_data.loc[mask, "Event"] = swimming_data.loc[mask, "Event"].str.replace(
        "m", "yds"
    )
    # remove the word yard from the event name
    swimming_data["Event"] = swimming_data["Event"].str.replace("yard ", "")

    return swimming_data


def capitalize_events(swimming_data: pd.DataFrame) -> pd.DataFrame:
    """Capitalize the event names in the swimming data."""

    swimming_data["Event"] = swimming_data["Event"].str.title()

    return swimming_data


def remove_athletes_from_relay(df: pd.DataFrame) -> pd.DataFrame:
    """Remove any individual athletes from relay results and
    remove any duplicate rows of countries for a relay medal.

    Args:
        df (pd.DataFrame): A dataframe wtih relay in the Events column.

    Returns:
        pd.DataFrame: A dataframe with the country name in the Athlete column for relays.
    """

    # get only the relay data
    relays_df = df[df["Event"].str.contains("Relay")]
    # group by the relevent columns to remove individual athletes from the relay results
    new_relays_df = (
        relays_df.groupby(
            [
                "Country",
                "NOC",
                "Season",
                "Year",
                "City",
                "Category",
                "Sport",
                "Event",
                "Medal",
            ]
        )
        .size()
        .reset_index(name="Medal_Count")
    )
    new_relays_df.drop(columns="Medal_Count", inplace=True)
    # create athlete column that is same as country column
    new_relays_df["Athlete"] = new_relays_df["Country"]

    # remove any rows with Relay in the Event name from the original df
    no_relays_df = df[~df["Event"].str.contains("Relay")]

    # set the no_relays_df columns to be the same as the new_relays_df columns
    new_relays_df = new_relays_df[no_relays_df.columns]

    # combine the two dataframes
    combined_df = pd.concat([no_relays_df, new_relays_df], ignore_index=True)

    return combined_df


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
    assert swimming_data["Event"].str.contains("×").sum() == 0


def test_assign_gender():
    swimming_data = extract_swimming_data(OLYMPICS_DATA_PATH)
    swimming_data = standardize_event_names(swimming_data)
    # check tokyo data naming conventions
    tokyo_swim = swimming_data[swimming_data["Year"] == 2020]
    tokyo_swim = assign_gender(tokyo_swim)
    assert tokyo_swim["Category"].isna().sum() == 0
    assert tokyo_swim["Category"].nunique() == 3
    # check paris data naming conventions
    paris_swim = swimming_data[swimming_data["Year"] == 2024]
    paris_swim = assign_gender(paris_swim)
    assert paris_swim["Category"].isna().sum() == 0
    assert paris_swim["Category"].nunique() == 3

    # check all others
    other_swim = swimming_data[
        (swimming_data["Year"] != 2020) & (swimming_data["Year"] != 2024)
    ]
    other_swim = assign_gender(other_swim)
    assert other_swim["Category"].isna().sum() == 0
    # mixed relay were not in the olympics before 2020
    assert other_swim["Category"].nunique() == 2


def test_remove_gender_from_event():
    test_df = pd.DataFrame(
        {
            "Event": ["men200m backstroke", "women100m freestyle"],
        }
    )
    test_df = remove_gender_from_event(test_df)
    assert test_df["Event"].to_list() == ["200m backstroke", "100m freestyle"]


def test_remove_apostrophes():
    test_df = pd.DataFrame(
        {"Event": ["'s 200m backstroke", "400m freestyle", "'s 200 butterfly"]}
    )
    test_df = remove_apostrophes(test_df)
    assert test_df["Event"].to_list() == [
        "200m backstroke",
        "400m freestyle",
        "200 butterfly",
    ]


def test_add_meters_to_event_name():
    test_df = pd.DataFrame(
        {"Event": ["200m backstroke", "4x100 freestyle relay", "200 butterfly"]}
    )
    test_df = add_meters_to_event_name(test_df)
    assert test_df["Event"].to_list() == [
        "200m backstroke",
        "4x100m freestyle relay",
        "200m butterfly",
    ]


def test_10km_open_water():
    test_df = pd.DataFrame({"Event": ["10m kilom open water", "200m butterfly"]})
    test_df = rename_10km_event(test_df)
    assert test_df["Event"].to_list() == [
        "10km open water",
        "200m butterfly",
    ]


def test_replace_meters_with_yards():
    test_df = pd.DataFrame(
        {
            "Event": [
                "400m yard backstroke",
                "4x100m freestyle relay",
                "200m yard butterfly",
            ]
        }
    )
    test_df = replace_meters_with_yards(test_df)
    assert test_df["Event"].to_list() == [
        "400yds backstroke",
        "4x100m freestyle relay",
        "200yds butterfly",
    ]


def test_capitalize_events():
    test_df = pd.DataFrame(
        {"Event": ["200m backstroke", "4x100m freestyle relay", "200m butterfly"]}
    )
    test_df = capitalize_events(test_df)
    assert test_df["Event"].to_list() == [
        "200M Backstroke",
        "4X100M Freestyle Relay",
        "200M Butterfly",
    ]


def test_remove_athletes_from_relay():

    test_df = pd.DataFrame(
        {
            "Country": [
                "United States",
                "United States",
                "Japan",
                "Japan",
                "Canada",
                "United States",
            ],
            "NOC": ["USA", "USA", "JPN", "JPN", "CAN", "USA"],
            "Season": ["Summer", "Summer", "Summer", "Summer", "Summer", "Summer"],
            "Year": [2020, 2020, 2020, 2020, 2020, 2020],
            "City": ["Tokyo", "Tokyo", "Tokyo", "Tokyo", "Tokyo", "Tokyo"],
            "Category": ["Men", "Men", "Men", "Men", "Men", "Men"],
            "Sport": [
                "Swimming",
                "Swimming",
                "Swimming",
                "Swimming",
                "Swimming",
                "Swimming",
            ],
            "Event": [
                "4x100m Relay",
                "4x100m Relay",
                "4x100m Relay",
                "4x100m Relay",
                "4x100m Relay",
                "100m Freestyle",
            ],
            "Athlete": [
                "John Doe",
                "Michael Phelps",
                "Hiroki Abe",
                "Kohei Uchimura",
                "Brian Johns",
                "Caeleb Dressel",
            ],
            "Medal": ["Gold", "Gold", "Silver", "Silver", "Bronze", "Gold"],
        }
    )

    output_df = remove_athletes_from_relay(test_df)
    assert output_df.shape == (4, 10)
    assert output_df["Event"].str.contains("Relay").sum() == 3
    assert output_df.columns.to_list() == [
        "Athlete",
        "Country",
        "NOC",
        "Season",
        "Year",
        "City",
        "Sport",
        "Event",
        "Medal",
        "Category",
    ]


if __name__ == "__main__":
    swimming_data = extract_swimming_data(OLYMPICS_DATA_PATH)
    swimming_data = standardize_event_names(swimming_data)
    swimming_data = assign_gender(swimming_data)
    swimming_data = remove_gender_from_event(swimming_data)
    swimming_data = remove_apostrophes(swimming_data)
    swimming_data = add_meters_to_event_name(swimming_data)
    swimming_data = rename_10km_event(swimming_data)
    swimming_data = capitalize_events(swimming_data)
    swimming_data = remove_athletes_from_relay(swimming_data)
    # save the data
    swimming_data.to_csv(SWIMMING_DATA_PATH, index=False)
