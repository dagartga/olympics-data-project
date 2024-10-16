# scrape the AP news website for the Paris 2024 Olympics tags
# https://apnews.com/article/olympics-2024-medal-winners-today-b9522fd1223ae6599569ffe1ee48cc62

import json

import requests
from bs4 import BeautifulSoup

AP_NEWS_URL = "https://apnews.com/article/olympics-2024-medal-winners-today-b9522fd1223ae6599569ffe1ee48cc62"


def scrape_ap_news(url):
    """Scrape the AP News Paris 2024 Olympic results
    Args:
        url (str): The URL of the AP News website
    Returns:
        dict: the <h2> and <p> tags from the website
            which contains the important information.
    """
    # comfirm the connection to the website
    response = requests.get(url)
    assert response.status_code == 200

    # get the class = RichTextStoryBody
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.find_all("div", class_="RichTextStoryBody")

    # get all the data in <h2> and <p> tags
    h2_tags = []
    p_tags = []
    for tags in text:
        for h2 in tags.find_all("h2"):
            h2_tags.append(h2.text)
        for p in tags.find_all("p"):
            p_tags.append(p.text)

    assert len(h2_tags) == 337
    assert len(p_tags) == 1138

    # combine the data in <h2> and <p> tags
    paris_data = {"h2": h2_tags, "p": p_tags}

    # save the data to a json file
    with open("data/raw/paris2024_results.json", "w") as file:
        json.dump(paris_data, file)


if __name__ == "__main__":
    scrape_ap_news(AP_NEWS_URL)
    print("AP News Paris Olympic data has been scraped and saved successfully.")
