import json

import pandas as pd
import requests
from bs4 import BeautifulSoup

FILE_PATH = "data/raw/country_codes.csv"
IBAN_URL = "https://www.iban.com/country-codes"


def scrape_iban_website(url: str) -> dict:
    """Scrape the IBAN website for a JSON object with the
    country name as the key and the country code and NOC nested
    in the JSON object.

    Args:
        url (str): url for the website with the country codes.
        Which is https://www.iban.com/country-codes.

    Returns:
        dict: the key is the country name and the value is
        a dictionary of the country code and NOC.

    Example:
        {
            "Afghanistan": {
                "country_code": "AF",
                "country_noc": "AFG"
            },
            "Albania": {
                "country_code": "AL",
                "country_noc": "ALB"
            },
            ...
    """
    # Send a GET request to the IBAN website
    response = requests.get(url)

    assert response.status_code == 200, "Failed to fetch web page"

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the <table> element with the class 'table table-bordered'
    table = soup.find("table", id="myTable")

    # Check if the table is found
    if table:
        # Find all <tr> tags within the table
        rows = table.find_all("tr")

        # Initialize a dictionary to store the country codes
        country_codes = {}

        # Iterate over each <tr> tag (each country)
        for row in rows:
            # Find all <td> tags within this <tr>
            cells = row.find_all("td")

            # The country name is key and the country code and NOC are nested values
            if cells:
                country_name = cells[0].get_text(strip=True)
                country_codes[country_name] = {
                    "country_code": cells[1].get_text(strip=True),
                    "country_noc": cells[2].get_text(strip=True),
                }

        return country_codes


def convert_country_codes_to_df(country_codes: dict) -> pd.DataFrame:
    """Convert the country codes dictionary to a pandas DataFrame."""
    country_codes_df = pd.DataFrame(country_codes).T
    country_codes_df.index.name = "country_name"
    country_codes_df.reset_index(inplace=True)
    return country_codes_df


def save_country_codes(country_codes: pd.DataFrame, file_path: str) -> None:
    """Save the country codes dictionary to a csv file."""
    country_codes.to_csv(file_path, index=False)


if __name__ == "__main__":
    country_codes = scrape_iban_website(IBAN_URL)
    country_codes_df = convert_country_codes_to_df(country_codes)
    save_country_codes(country_codes_df, FILE_PATH)
    print("Country codes saved to data/raw/country_codes.csv")
