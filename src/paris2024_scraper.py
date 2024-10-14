import json

import requests
from bs4 import BeautifulSoup

# URL to scrape
BASE_URL = "https://www.lemonde.fr/en/sport/jo-2024/results/"


def get_paris_results(url):
    """Get the results of the Paris 2024 Olympics from the given URL.
    Args:
        url (str): The URL to scrape.

    Returns:
        dict: A dictionary containing the scraped data.
    """

    # store the scraped data
    medal_results = {}

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Find all div elements with class "sport-block js-sport-block"
        sport_blocks = soup.find_all("div", class_="sport-block js-sport-block")

        # Iterate through the sport blocks
        for block in sport_blocks:
            # Find the h2 element with class "sport-block__name"
            h2_tag = block.find("h2", class_="sport-block__name")
            if h2_tag:
                # get the main sport name, such as "Gymnastics"
                sport_name = h2_tag.get_text(strip=True)

            subcategories = block.find_all(
                "div", class_="sport-calendar-cell js-jo-cell"
            )
            for subcategory in subcategories:
                # get the subcategory, such as "Floor Exercise (M)"
                sub_cat_name = subcategory.find(
                    "div", class_="sport-calendar-cell__title"
                ).get_text(strip=True)
                medal_results[sport_name] = {sub_cat_name: []}

                class_participants = subcategory.find_all(
                    "div", class_="sport-participant"
                )
                for class_participant in class_participants:
                    participant_name = class_participant.find(
                        "div", class_="sport-participant__name"
                    ).get_text(strip=True)
                    medal_text = class_participant.find(
                        "div", class_="sport-participant__status"
                    )
                    span_tag = medal_text.find("span")
                    medal = span_tag["class"][0]
                    medal = medal.split("-")[-1]
                    # Find the img tag with class "sport-participant__img"
                    img_tag = class_participant.find(
                        "img", class_="sport-participant__img"
                    )

                    # Extract the src attribute
                    if img_tag:
                        img_src = img_tag["src"]
                        country_code = img_src.split("/")[-1].replace(".svg", "")

                    medal_results[sport_name][sub_cat_name].append(medal)
                    medal_results[sport_name][sub_cat_name].append(participant_name)
                    medal_results[sport_name][sub_cat_name].append(country_code)

    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

    return medal_results


if __name__ == "__main__":
    # Get the event results
    paris_results = get_paris_results(BASE_URL)
    # save the dictionary to a JSON file
    with open("./data/raw/paris2024_medals.json", "w") as f:
        json.dump(paris_results, f, indent=4)

    print("Medal results saved to data/raw/paris2024_medals.json")
