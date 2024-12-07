import pandas as pd
import requests
from bs4 import BeautifulSoup
from pprint import pprint
import codecs
import random
from tqdm import tqdm

from parsing.utils import clean_text


def get_mechanics(sample=None):
    res = []
    url = "https://dnd.su/articles/mechanics/"
    r = requests.get(url)
    r.encoding = "utf-8"
    if not (r):
        print("not found", url)
    soup = BeautifulSoup(r.text)

    if sample:
        ar = random.sample(soup.find_all("a", {"class": "read-more"}), sample)
    else:
        ar = soup.find_all("a", {"class": "read-more"})

    for one in tqdm(ar):
        mechanic_link = "https://dnd.su" + one["href"]
        mechanic_link = requests.get(mechanic_link)

        mechanic_soup = BeautifulSoup(mechanic_link.text, "html.parser")

        name = mechanic_soup.find("h2", {"class": "card-title"})
        name = "\n".join([clean_text(x) for x in name.findAll(text=True)]) if name else None

        description = mechanic_soup.find("div", {"class": "card__body new-article"})
        description = clean_text(description.get_text()) if description else None
        _fragments = mechanic_soup.find("div", {"class": "desc card__article-body"})

        fragments = []
        fragment = ""
        for one in _fragments.findAll():

            if one.name in ["h1", "h2", "h3", "h4"]:
                if fragment != "":
                    fragments.append(fragment)
                    fragment = ""

            fragment = fragment + clean_text(one.get_text())

        out = {"name": name, "description": description, "fragments": fragments}

        res.append(out)

    return res
