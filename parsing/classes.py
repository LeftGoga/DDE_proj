import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm  # Import tqdm

from parsing.utils import clean_text


def get_items():
    items = []
    url = "https://dnd.su/items/"
    r = requests.get(url)
    r.encoding = "utf-8"
    if not (r):
        print("not found", url)
    soup = BeautifulSoup(r.text)

    # Find all item links first
    item_links = [one["href"] for one in soup.find_all("a", {"class": "list-item-wrapper"})]

    # Use tqdm to show progress bar for each item
    for item_link in tqdm(item_links, desc="Processing items", unit="item"):
        item_url = "https://dnd.su" + item_link
        item_r = requests.get(item_url)
        item_soup = BeautifulSoup(item_r.text, "html.parser")

        item_name = clean_text(item_soup.find("h1").text if item_soup.find("h1") else "Unnamed Item")
        item_cost = item_soup.find("li", {"class": "price"})
        if item_cost:
            item_cost = clean_text(item_cost.get_text())
            item_cost = item_cost[item_cost.find(":"):].strip()
        else:
            item_cost = None

        item_type = item_soup.find("li", {"class": "size-type-alignment"})
        if item_type:
            item_type = clean_text(item_type.get_text())
        else:
            item_type = None

        item_description = item_soup.find("li", {"class": "subsection desc"})
        if item_description:
            item_description = [clean_text(x.get_text()) for x in item_description.find_all("p")]
        else:
            item_description = []

        item = {"name": item_name, "cost": item_cost, "type": item_type, "description": item_description}
        print(item)  # Optional: You can choose to log this instead of print
        items.append(item)

    return items


if __name__ == "__main__":
    get_items()
