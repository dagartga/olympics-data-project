import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL to scrape
BASE_URL = "https://www.olympedia.org/editions/61/result"
# Base URL for the links
LINK_BASE = "https://www.olympedia.org"


def get_sports_links(url):
    """Get the links to the sports from the given URL.
    Args:
        url (str): The base URL to scrape.

    Returns:
        pd.DataFrame: A DataFrame containing the hrefs and their corresponding text.
    """

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the table with class 'table'
        table = soup.find("table", class_="table")

        # Check if table is found
        if table:
            # Find all <a> tags within the table
            links = table.find_all("a")

            # Extract hrefs and their corresponding text
            data = []
            for link in links:
                href = link.get("href")
                # add the base to the href
                href = LINK_BASE + href
                text = link.get_text(strip=True)  # Strip whitespace from the text
                data.append({"href": href, "text": text})

            # Create a pandas DataFrame from the extracted data
            df = pd.DataFrame(data)

            # Return the DataFrame
            return df
        else:
            print("Table with class 'table' not found.")
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")




if __name__ == "__main__":
    # Get the sports links
    sports_links = get_sports_links(BASE_URL)

    # save the DataFrame to a CSV file
    sports_links.to_csv("../data/raw/tokyo2020_links.csv", index=False)