import requests
from bs4 import BeautifulSoup
import json
import time
import random
from tqdm import tqdm

def clean_text(text):

    return ' '.join(text.split())

def get_monster_links(session):

    base_url = "https://dnd.su"
    bestiary_url = f"{base_url}/bestiary/"
    try:
        response = session.get(bestiary_url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {bestiary_url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    monster_links = {base_url + link['href'] for link in soup.find_all("a", href=True) if link['href'].startswith('/bestiary/') and link['href'] != '/bestiary/'}
    return list(monster_links)

def parse_monster_page(url, session):
    try:
        response = session.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    monster_data = {
        'Name': None,
        'Stats': {},
        'Source': None,
        'Abilities': [],
        'Actions': [],
        'Description': None
    }


    name_section = soup.find('div', class_='card__header')
    if name_section:
        name_element = name_section.find('h2', class_='card-title')
        monster_data['Name'] = clean_text(name_element.text) if name_element else None


    stats_section = soup.find_all('li')
    for stat in stats_section:
        strong_element = stat.find('strong')
        if strong_element:
            key = clean_text(strong_element.text)
            value = clean_text(stat.get_text(strip=True).replace(key, ''))

            if not value and '+' in key:
                parts = key.split('+', 1)
                key = clean_text(parts[0])

            if "Источник" in key:
                monster_data['Source'] = value
            elif any(kw in key for kw in ["Класс Доспеха", "Хиты", "Скорость", "Чувства", "Языки", "Опасность", "Бонус мастерства"]):
                monster_data['Stats'][key] = value
            elif key in ["Уязвимость к урону", "Иммунитет к урону"]:
                monster_data['Stats'][key] = value
            else:
                if "Спасброски" in key or "Навыки" in key:
                    monster_data['Stats'][key] = value
                elif key.endswith("."):
                    monster_data['Abilities'].append(f"{key} {value}")

    abilities_section = soup.find_all('li', class_='subsection desc')
    for ability in abilities_section:
        text = clean_text(ability.get_text(strip=True))
        if "Действия" not in text and "Описание" not in text:
            monster_data['Abilities'].append(text)


    actions_section = soup.find('h3', class_='subsection-title', string="Действия")
    if actions_section:
        action_divs = actions_section.find_next_siblings('div')
        for action in action_divs:
            monster_data['Actions'].append(clean_text(action.get_text(strip=True)))


    description_section = soup.find('h3', class_='subsection-title', string="Описание")
    if description_section:
        description_div = description_section.find_next('div')
        if description_div:
            monster_data['Description'] = clean_text(description_div.get_text(strip=True))

    return monster_data

def get_monsters(sample=None):

    with requests.Session() as session:
        monster_links = get_monster_links(session)
        if not monster_links:
            print("No monster links found.")
            return

        if sample:
            if sample > len(monster_links):
                print(f"Requested sample size {sample} exceeds available monsters ({len(monster_links)}). Using full list.")
                sample = len(monster_links)
            monster_links = random.sample(monster_links, sample)

        all_monsters = []
        print(f"Parsing {len(monster_links)} monsters...")
        for link in tqdm(monster_links, desc="Parsing Monsters", unit="monster"):
            monster_data = parse_monster_page(link, session)
            if monster_data:
                all_monsters.append(monster_data)


        # with open("bestiary_noconcat.json", "w", encoding="utf-8") as f:
        #     json.dump(all_monsters, f, ensure_ascii=False, indent=2)
        # print("Bestiary data saved to bestiary_noconcat.json")

        return all_monsters
if __name__ == "__main__":
    get_monsters()
