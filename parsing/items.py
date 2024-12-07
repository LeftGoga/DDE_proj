import pandas as pd
import requests
from bs4 import BeautifulSoup
import random
from tqdm import tqdm

from parsing.utils import clean_text


def get_items():
    items = []
    url = "https://dnd.su/items/"
    r = requests.get(url)
    r.encoding = "utf-8"
    if not (r):
        print("not found", url)
    soup = BeautifulSoup(r.text)
    # print(soup)
    for one in tqdm(soup.find_all("a", {"class": "list-item-wrapper"})):
        item_name = one.find("div").text
        item_link = "https://dnd.su" + one["href"]

        item_r = requests.get(item_link)

        item_soup = BeautifulSoup(item_r.text, "html.parser")

        item_cost = item_soup.find("li", {"class": "price"})
        if item_cost:
            item_cost = clean_text(item_cost.get_text())
            item_cost = item_cost[item_cost.find(":") :].strip()
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
        # print(item)
        items.append(item)

    return items


if __name__ == "__main__":
    get_items()
