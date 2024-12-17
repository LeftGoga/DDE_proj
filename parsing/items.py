import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from parsing.utils import clean_text

def get_items(sample_size=50):
    url = "https://dnd.su/items/"
    r = requests.get(url)
    r.encoding = "utf-8"
    if not r.ok:
        print("Failed to fetch main page", url)
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    item_links = ["https://dnd.su" + link["href"] for link in soup.find_all("a", {"class": "list-item-wrapper"})]

    # Limit the number of links to the sample size
    item_links = item_links[:sample_size]

    items = []
    for item_url in tqdm(item_links, desc="Scraping items", unit="item"):
        item_r = requests.get(item_url)
        item_soup = BeautifulSoup(item_r.text, "html.parser")

        item = {
            "name": clean_text(item_soup.find("h1").text) if item_soup.find("h1") else "Unnamed Item",
            "cost": clean_text(item_soup.find("li", {"class": "price"}).get_text().split(":", 1)[-1].strip())
            if item_soup.find("li", {"class": "price"}) else None,
            "type": clean_text(item_soup.find("li", {"class": "size-type-alignment"}).get_text())
            if item_soup.find("li", {"class": "size-type-alignment"}) else None,
            "description": [
                clean_text(p.get_text())
                for p in item_soup.find("li", {"class": "subsection desc"}).find_all("p")
            ] if item_soup.find("li", {"class": "subsection desc"}) else []
        }
        items.append(item)


    return items

if __name__ == "__main__":
    get_items()
