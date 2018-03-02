"""Get Townsville Ross River Dam Level from Website."""

import json
import requests

URL = "https://mitownsville.service-now.com/webapps/dam_levels.do"
START_STRING = "var ross_last_reading"


def main():
    # Get response text from Council website
    response = requests.get(URL)
    text = response.text
    print(text)
    # Extract just the JSON-like string that contains the current data
    start_index = text.find(START_STRING) + len(START_STRING) + 4
    finished_index = text.find("}", start_index) + 1
    section = text[start_index:finished_index].replace("\\", "")
    # Convert JSON text to dictionary and display the value without the '%'
    data = json.loads(section)
    # data looks like {'date': '01/03/2018 09:00:00', 'percent': '63%', 'volume': '146124 ML'}
    print(data["percent"][:-1])


main()
