import requests
from bs4 import BeautifulSoup
import pandas as pd
import json



def scrape_events_medals(url):
    """Scrape the medals results for each event from the given URL.
    Args:
        url (str): The URL to scrape.
        
    Returns:
        dict: A dictionary containing the event names as keys and a list of medal winners as values.
    
    """
    # store the medals results in a dictionary
    medals_dict = {}

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
    
        # Find the <h2> tag with the exact text "Medals"
        medals_h2 = soup.find('h2', string='Medals')
    
        # Check if the <h2> tag is found
        if medals_h2:
            # Find the next <table> element after the <h2> tag
            medals_table = medals_h2.find_next('table', class_='table table-striped')
        
            # Check if the table is found
            if medals_table:
                # Find all <tr> tags within the table
                rows = medals_table.find_all('tr')
            
                # Iterate over each <tr> tag (each event)
                for row in rows:
                    # Find all <a> tags within this <tr>
                    links = row.find_all('a')
                
                    # Group the event's href links and their text
                    event_data = []
                    for link in links:
                        href = link.get('href')
                        text = link.get_text(strip=True)
                        event_data.append({'href': href, 'text': text})
                
                    # Print the event data for each row
                    if event_data:
                        for i, data in enumerate(event_data):
                            if i == 0:
                                medals_dict[data['text']] = []
                            else:
                                medals_dict[event_data[0]['text']].append(data['text'])
            else:
                print("No table found after the 'Medals' heading.")
        else:
            print("<h2> with text 'Medals' not found.")
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    
    return medals_dict    

if __name__ == '__main__':
    
    # load the links from the data/raw/tokyo2020_links.csv
    sports_links_df = pd.read_csv('./data/raw/tokyo2020_links.csv')
    
    # create a dictionary to store the medal results
    tokyo2020_medals = {}
    
    # iterate over the sports links
    for row in sports_links_df.itertuples():
        sport_name = row.text
        sport_link = row.href
        
        # if the url has editions then it is a sport category, not an event link
        if "editions" in sport_link:
            print(f"Scraping medal results for {sport_name}...")
            medal_results = scrape_events_medals(sport_link)
            tokyo2020_medals[sport_name] = medal_results
        
    # save the dictionary to a JSON file
    with open('./data/raw/tokyo2020_medals.json', 'w') as f:
        json.dump(tokyo2020_medals, f, indent=4)
        
    print("Medal results saved to data/raw/tokyo2020_medals.json")