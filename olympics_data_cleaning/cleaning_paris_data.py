import csv
import json
import re

# Extract the year from the filename using regex
filename = "data/raw/paris2024_medals.json"
year_match = re.search(r"\d{4}", filename)
year = year_match.group(0) if year_match else "Unknown"

# Load the JSON data
with open(filename, "r") as file:
    data = json.load(file)

# Prepare the CSV file
with open("data/processed/paris2024_medal.csv", "w", newline="") as csvfile:
    fieldnames = [
        "Athlete/Team",
        "Country_Code",
        "Year",
        "Season",
        "Sport",
        "Event",
        "Medal",
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()

    # Iterate through the JSON data
    for sport, events in data.items():
        for event, results in events.items():
            for i in range(0, len(results), 3):
                medal = results[i]
                athlete = results[i + 1]
                country = results[i + 2]
                writer.writerow(
                    {
                        "Athlete/Team": athlete,
                        "Country_Code": country,
                        "Year": year,
                        "Season": "Summer",
                        "Sport": sport,
                        "Event": event,
                        "Medal": medal,
                    }
                )

print("CSV file has been created successfully.")
