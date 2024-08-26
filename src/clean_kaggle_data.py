import pandas as pd


KAGGLE_DATA_PATH = "data/raw/athlete_events.csv"
CLEAN_DATA_PATH = "data/processed/kaggle_1896_2016_results.csv"
FINAL_COLUMNS = [
    "Name",
    "Team",
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
    """Remove unnecessary columns."""
    return df[FINAL_COLUMNS]


def save_data(df: pd.DataFrame, path: str) -> None:
    """Save the cleaned dataset to the specified path."""
    df.to_csv(path, index=False)


########################################################################
# Tests
########################################################################


def test_data_import():
    df = import_data(KAGGLE_DATA_PATH)
    assert not df.empty, "Dataframe is empty"
    assert len(df) == 271116, f"Expected 271116 rows but got {len(df)}"
    assert len(df.columns) == 15, f"Expected 15 columns but got {len(df.columns)}"


def test_remove_null_medals():
    df = import_data(KAGGLE_DATA_PATH)
    df = remove_null_medals(df)
    assert len(df) == 39783, f"Expected 39783 rows but got {len(df)}"


def test_remove_winter_olympics():
    df = import_data(KAGGLE_DATA_PATH)
    df = remove_winter_olympics(df)
    assert df["Season"].unique() == ["Summer"], "Expected only Summer Olympics data"


def test_final_columns():
    df = import_data(KAGGLE_DATA_PATH)
    df = remove_null_medals(df)
    df = remove_winter_olympics(df)
    df = remove_columns(df)
    assert len(df.columns) == 9, f"Expected 9 columns but got {len(df.columns)}"
    assert (
        df.columns.tolist() == FINAL_COLUMNS
    ), f"Expected columns {FINAL_COLUMNS} but got {df.columns.tolist()}"


if __name__ == "__main__":
    print("Cleaning Kaggle Olympic (1896-2016) data...")
    df = import_data(KAGGLE_DATA_PATH)
    df = remove_null_medals(df)
    df = remove_winter_olympics(df)
    df = remove_columns(df)
    save_data(df, CLEAN_DATA_PATH)
    print(f"Kaggle Olympic (1896-2016) data saved to {CLEAN_DATA_PATH}")
