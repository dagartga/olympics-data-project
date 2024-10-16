from pathlib import Path

import pandas as pd

# Get the current script's directory
base_dir = Path(__file__).parent
# convert the path to the project directory
project_dir = base_dir.parent

# Construct the path to the data csv files
KAGGLE_DATA_PATH = project_dir / "data" / "raw" / "athlete_events.csv"
CLEAN_DATA_PATH = project_dir / "data" / "processed" / "kaggle1896_to_2016_results.csv"

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


def import_data(path: str) -> pd.DataFrame:
    """Import the Olympics dataset from the specified path."""
    return pd.read_csv(path)


def remove_null_medals(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows with NaN values in the 'Medal' column."""
    return df.dropna(subset=["Medal"])


def remove_winter_olympics(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only Summer Olympics data."""
    return df[df["Season"] == "Summer"]


def remove_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remove unnecessary columns and rename Team as Country
    and Name as Athlete."""
    df = df.rename(columns={"Team": "Country"})
    df = df.rename(columns={"Name": "Athlete"})
    return df[FINAL_COLUMNS]


def remove_hyphen_numbers(df: pd.DataFrame) -> pd.DataFrame:
    """Remove Country names that end in -1, -2, -3."""
    # use regex to remove any Team names that end in -1, -2, -3
    df["Country"] = df["Country"].str.replace(r"-\d", "", regex=True)
    return df


def save_data(df: pd.DataFrame, path: str) -> None:
    """Save the cleaned dataset to the specified path."""
    df.to_csv(path, index=False)


if __name__ == "__main__":
    print("Cleaning Kaggle Olympic (1896-2016) data...")
    df = import_data(KAGGLE_DATA_PATH)
    df = remove_null_medals(df)
    df = remove_winter_olympics(df)
    df = remove_columns(df)
    df = remove_hyphen_numbers(df)
    save_data(df, CLEAN_DATA_PATH)
    print(f"Kaggle Olympic (1896-2016) data saved to {CLEAN_DATA_PATH}")
