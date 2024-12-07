import requests
from bs4 import BeautifulSoup
from pprint import pprint
from tqdm import tqdm
import html2text

from parsing.utils import clean_text  # Assuming this is your custom cleaning function

def get_dop_info(sample=None):
    ar = [
        "https://dnd.su/articles/newbie/468-using-ability-scores/",
        "https://dnd.su/articles/newbie/26-main-formulas/",
        "https://dnd.su/articles/newbie/564-faq/",
        "https://dnd.su/articles/newbie/536-how-to-start-playing-dd/",
    ]
    res = []
    for one in tqdm(ar):
        # Fetch the page content
        mechanic_link = requests.get(one)
        mechanic_soup = BeautifulSoup(mechanic_link.text, "html.parser")

        # Extract and clean the name
        name = mechanic_soup.find("h2", {"class": "card-title"})
        name = "\n".join([clean_text(x) for x in name.findAll(text=True)]) if name else None

        # Extract and convert description to Markdown
        description_html = mechanic_soup.find("div", {"class": "card__body new-article"})
        if description_html:
            # Use html2text to convert to Markdown
            html_converter = html2text.HTML2Text()
            html_converter.ignore_links = False  # Keep links in Markdown
            description_markdown = html_converter.handle(str(description_html))
        else:
            description_markdown = None

        # Append the result
        out = {"name": name, "description": description_markdown}
        res.append(out)

    return res

if __name__ == "__main__":
    result = get_dop_info()
    print(result)