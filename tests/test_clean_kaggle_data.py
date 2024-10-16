import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from olympics_data_project.data_cleaning.clean_kaggle_data import (
    import_data,
    KAGGLE_DATA_PATH,
    remove_null_medals,
    remove_winter_olympics,
    remove_columns,
    FINAL_COLUMNS,
    remove_hyphen_numbers,
)


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


def test_remove_hyphen_numbers():
    df = import_data(KAGGLE_DATA_PATH)
    df = remove_null_medals(df)
    df = remove_winter_olympics(df)
    df = remove_columns(df)
    df = remove_hyphen_numbers(df)
    assert (
        "United States-1" not in df["Country"].values
    ), "Country names still contain -1"
    assert (
        not df["Country"].str.contains(r"-\d").any()
    ), "Country names still contain hyphen numbers"
