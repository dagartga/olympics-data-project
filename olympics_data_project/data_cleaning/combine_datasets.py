from pathlib import Path

import pandas as pd

# Get the current script's directory
base_dir = Path(__file__).parent
# convert the path to the project directory
project_dir = base_dir.parent

# Construct the path to the necessary files
TOKYO_PATH = project_dir / "data" / "processed" / "tokyo2020_results.csv"
PARIS_PATH = project_dir / "data" / "processed" / "paris2024_results.csv"
KAGGLE_PATH = project_dir / "data" / "processed" / "kaggle1896_to_2016_results.csv"
SAVE_PATH = project_dir / "data" / "processed" / "all_olympics_data.csv"


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


def save_combined_data() -> None:
    """Save the combined paris, tokyo, and kaggle datasets to
    a csv file."""
    combined_data = combine_datasets()
    combined_data = format_the_strings(combined_data)
    combined_data.to_csv(SAVE_PATH, index=False)


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

def format_the_strings(data: pd.DataFrame) -> pd.DataFrame:
    """Format the strings in the dataframe to be title case.
    Example: "united states" -> "United States"
    """
    
    columns = ["Athlete", "Country", "Season", "City", "Sport", "Event", "Medal"]
    
    for column in columns:
        data[column] = data[column].str.title() 
    
    return data


if __name__ == "__main__":
    save_combined_data()
