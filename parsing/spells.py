import pandas as pd
import requests
from bs4 import BeautifulSoup
from pprint import pprint
import codecs
import random
from tqdm import tqdm

from parsing.utils import clean_text
import json

def parse_spells_cards(url = "https://dnd.su/spells/"):
    # Fetch the webpage content
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception if the request fails

    # Parse the page using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the script tag containing the "window.LIST" object
    script_tag = soup.find('script', text=lambda t: t and 'window.LIST' in t)
    if not script_tag:
        raise ValueError("Couldn't find the script containing 'window.LIST'.")

    # Extract the JSON-like string from the script tag
    script_content = script_tag.string
    start_index = script_content.find('window.LIST = ') + len('window.LIST = ')
    end_index = script_content.rfind(';')
    json_data = script_content[start_index:end_index]

    # Parse the JSON data
    data = json.loads(json_data)

    # Extract the "cards" entry
    cards = data.get('cards', [])

    # Create a list of spell information from "cards"
    spells = [card for card in cards]

    # Save the structured JSON to a file
    with open("spells.json", "w", encoding="utf-8") as f:
        json.dump(spells, f, ensure_ascii=False, indent=4)


def get_spells(sample=10):
    parse_spells_cards()
    res = []
    with open("C:\\Users\\leftg\\PycharmProjects\\data_engineering\\parsing\\spells.json", "r", encoding="utf-8") as f:
        spells = json.loads(f.read())
    if sample:
        ar = random.sample(spells, sample)
    else:
        ar = spells

    for one in tqdm(ar):
        link = "https://dnd.su" + one["link"]
        response = requests.get(link)
        if response.status_code != 200:
            print(f"Failed to fetch {link}, status code: {response.status_code}")
            continue

        link_soup = BeautifulSoup(response.text, "html.parser")
        name = link_soup.find("h2", {"class": "card-title"})
        name = "\n".join([clean_text(x.text) for x in name.findAll(text=True)]) if name else None

        description = ""
        table = link_soup.find("ul", {"class": "params card__article-body"})
        if table:
            for item in table.find_all("li"):
                description += clean_text(item.text)
                description += "\n"
            description = description.replace("TCE", "")
        else:
            print(f"Warning: No description table found for {one.get('name')}")

        one["description"] = description
        one["name"] = name
        res.append(one)

    return res
if __name__ =="__main__":
    get_spells()