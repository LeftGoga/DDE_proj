import pandas as pd
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List
import json
from loguru import logger
import torch
import re
from datetime import datetime as time
from configs import model_name
device = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Device used: {device}")


model_params={"device":device}
embed_fun = HuggingFaceEmbeddings(model_name=model_name, model_kwargs = model_params)
logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=''),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO",
)

def create_splits(doc, embed_fun = embed_fun) -> List:

    text_splitter = SemanticChunker(embed_fun, breakpoint_threshold_type="standard_deviation")



    chunks = text_splitter.split_text(doc)
    embeddings = embed_fun.embed_documents(chunks)

    return chunks, embeddings


def preprocess_rules(df_mech):
    logger.info("Starting preprocessing for rules.")
    start = time.now()
    df_mech = df_mech.drop("fragments", axis=1)
    def extract_sources_section(text):
        start_symbols = ["\nИсточник:", "\nИсточники:"]

        start_index = -1
        for symbol in start_symbols:
            start_index = text.find(symbol)
            if start_index != -1:
                start_symbol = symbol
                break

        if start_index == -1:
            return []

        start_index += len(start_symbol)

        end_index = text.find("\n", start_index)
        if end_index == -1:
            end_index = len(text)

            # Extract the sources and split into a list
        sources = text[start_index:end_index].strip()
        return [source.strip() for source in sources.split(",")]

    def delete_sources_section(text):
        # Possible starting symbols
        start_symbols = ["\nИсточник:", "\nИсточники:"]

        start_index = -1
        for symbol in start_symbols:
            start_index = text.find(symbol)
            if start_index != -1:
                start_symbol = symbol
                break

        if start_index == -1:
            return text

        start_index += len(start_symbol)

        end_index = text.find("\n", start_index)
        if end_index == -1:
            end_index = len(text)

        updated_text = text[:text.find(start_symbol)] + text[end_index:]

        return updated_text.strip()

    def clean_desc(string):
        return string.replace("\n", " ")

    df_mech["source"] = df_mech["description"].apply(lambda x: extract_sources_section(x))
    df_mech["description"] = df_mech["description"].apply(lambda x: delete_sources_section(x))
    df_mech["description"] = df_mech["description"].apply(lambda x: clean_desc(x))

    logger.info(f"rules preprocessing finished. Time elapsed: {time.now() - start}")
    return df_mech


def preprocess_basics(df_basics):
    logger.info("Starting preprocessing for basics.")
    start = time.now()
    def extract_sources_section(text):

        start_symbols = ["**Источник:**"]

        start_index = -1
        for symbol in start_symbols:
            start_index = text.find(symbol)
            if start_index != -1:
                start_symbol = symbol
                break

        if start_index == -1:
            return None

        start_index += len(start_symbol)
        end_index = text.find("\n", start_index)
        if end_index == -1:
            end_index = len(text)

        sources = text[start_index:end_index].strip()
        return [source.strip() for source in sources.split(",")]

    def delete_sources_section(text):
        # Possible starting symbols
        start_symbols = ["**Источник:**"]

        start_index = -1
        for symbol in start_symbols:
            start_index = text.find(symbol)
            if start_index != -1:
                start_symbol = symbol
                break

        if start_index == -1:
            return text

        start_index += len(start_symbol)

        end_index = text.find("\n", start_index)
        if end_index == -1:
            end_index = len(text)

        updated_text = text[:text.find(start_symbol)] + text[end_index:]
        return updated_text.strip()

    def clean_desc(string):
        return string.replace("*", "").replace("\n", "")

    df_basics["source"] = df_basics["description"].apply(lambda x: extract_sources_section(x))
    df_basics["description"] = df_basics["description"].apply(lambda x: delete_sources_section(x))
    df_basics["description"] = df_basics["description"].apply(lambda x: clean_desc(x))
    logger.info(f"rules preprocessing finished.Time elapsed: {time.now() - start}")
    return df_basics

def preprocess_bestiary(df_bestiary):
    logger.info("Starting preprocessing for bestiary.")
    start = time.now()
    df_bestiary.columns = [col.split('.')[-1] for col in df_bestiary.columns]
    if "Иммунитет к урону" not in  df_bestiary.columns:
        df_bestiary["Иммунитет к урону"] = " "
    if "Уязвимость к урону" not in df_bestiary.columns:
        df_bestiary["Уязвимость к урону"] = " "
    if "Языки:" in df_bestiary.columns:
        df_bestiary = df_bestiary.drop("Языки:",axis=1)
    if "" in df_bestiary.columns:
        df_bestiary = df_bestiary.drop("",axis=1)
    df_bestiary["search_desc"] = df_bestiary["Name"] + " " + df_bestiary["Description"].fillna("") + " " + df_bestiary[
        "Иммунитет к урону"].fillna("") + " " + \
                                 df_bestiary["Уязвимость к урону"].fillna("")
    df_bestiary["Бонус мастерства"] = df_bestiary["Бонус мастерства"].astype(str)
    cols_fill = ["Спасброски", "Уязвимость к урону", "Иммунитет к урону", "Навыки", "Description", "Source", "Языки",
                 "Чувства"]
    df_bestiary[cols_fill] = df_bestiary[cols_fill].fillna("")
    cols_fill = ["Скорость", "Опасность"]
    df_bestiary[cols_fill] = df_bestiary[cols_fill].fillna(0)
    df_bestiary[["Abilities", "Actions"]] = df_bestiary[["Abilities", "Actions"]].fillna("").apply(list)
    df_bestiary = df_bestiary[~(df_bestiary["Name"] == "Комментарии")]
    logger.info(f"bestiary preprocessing finished.Time elapsed: {time.now() - start}")
    return df_bestiary

def preprocess_spells(df_spells):
    logger.info("Starting preprocessing for spells.")
    start = time.now()
    to_remove = ['title_sort', 'item_prefix', 'item_prefix_title', 'item_tags', 'item_suffix', 'item_icon',
                 'item_icon_title', 'filter_text',
                 'filter_level',
                 'filter_class', 'filter_class_tce', 'filter_archetype', 'filter_source',
                 'filter_school', 'filter_concentration', 'filter_ritual',
                 'filter_components', 'filter_casttime', 'filter_damtype', 'filter', "name"]
    df_spells = df_spells.drop(to_remove, axis=1)
    def extract_spell_details(spell_text):

        patterns = {
            "cast": r"Время накладывания:\s*([^\n]+)",
            "dist": r"Дистанция:\s*([^\n]+)",
            "comp": r"Компоненты:\s*([^\n]+)",
            "duration": r"Длительность:\s*([^\n]+)",
            "classes": r"Классы:\s*([^\n]+)",
            "source": r"Источник:\s*([^\n]+)"
        }

        extracted_data = {key: None for key in patterns.keys()}

        for key, pattern in patterns.items():
            match = re.search(pattern, spell_text)
            if match:
                extracted_data[key] = match.group(1).strip()

        description_start = re.search(r"Источник:\s*[^\n]+", spell_text)
        if description_start:
            start_index = description_start.end()
            description = spell_text[start_index:].strip()
            extracted_data["desc"] = description
        else:
            extracted_data["desc"] = None

        return tuple(extracted_data.values())

    def parse_spells(df):
        try:
            result = df["description"].apply(extract_spell_details)
            df[["cast", "dist", "comp", "duration", "classes", "source", "desc"]] = pd.DataFrame(result.tolist(),
                                                                                                 columns=["cast",
                                                                                                          "dist",
                                                                                                          "comp",
                                                                                                          "duration",
                                                                                                          "classes",
                                                                                                          "source",
                                                                                                          "desc"])
            return df
        except Exception as e:
            print("Error during processing:", str(e))
            return df

    df_spells = parse_spells(df_spells)
    df_spells=df_spells.fillna("")
    df_spells = df_spells.drop("description", axis=1)

    def clean_level(string):
        if string == "Заговор":
            return 0
        else:
            return int(string)

    df_spells["level"] = df_spells["level"].apply(lambda x: clean_level(x))
    logger.info(f"spells preprocessing finished.Time elapsed: {time.now() - start}")
    return df_spells


def preprocess_items(df_items):
    logger.info("Starting preprocessing for items.")
    start = time.now()
    def clean_name(string):
        string = string.replace("\n", "").replace("\t", "").replace("\r", "").replace("Магические предметы", "")
        return string

    def clean_cost(string):
        if isinstance(string, str):
            string = string.replace(":", "").replace(" ", "")

            return string
        else:
            return None

    def clean_description(string):

        string = " ".join(string)
        return string

    def cost_to_list(value):
        if value is None:
            return None

        match = re.match(r"(\d+)-(\d+)", value)
        if match:
            start, end = map(int, match.groups())
            return [start, end]
        return None  # Return None for invalid formats
    df_items["name"] = df_items["name"].apply(lambda x: clean_name(x))
    df_items["cost"] = df_items["cost"].apply(lambda x: clean_cost(x))
    df_items["description"] = df_items["description"].apply(lambda x: clean_description(x))
    df_items["cost"] = df_items["cost"].apply(cost_to_list)
    df_items["cost"] = df_items["cost"].fillna("").apply(list)
    logger.info(f"items preprocessing finished.Time elapsed: {time.now() - start}")
    return df_items



def preprocess_all():
    logger.info("Starting preprocessing all.")
    start = time.now()
    df_mech = pd.read_json("C:\\Users\\leftg\\PycharmProjects\\data_engineering\\data\\mechanics.json")
    df_mech = preprocess_rules(df_mech)
    df_basics = pd.read_json("C:\\Users\\leftg\\PycharmProjects\\data_engineering\\data\\basics.json")
    df_basics = preprocess_basics(df_basics)
    df_rules = pd.concat([df_basics, df_mech], axis=0)

    df_rules['chunks'], df_rules["embeddings"] = zip(*df_rules['description'].map(lambda x: create_splits(x)))

    chunked_rules = df_rules.explode(['chunks', "embeddings"]).reset_index(drop=True)
    chunked_rules.to_csv("C:\\Users\\leftg\\PycharmProjects\\data_engineering\\data\\rules.csv", index=False,na_rep=" ")

    with open('C:\\Users\\leftg\\PycharmProjects\\data_engineering\\data\\bestiary.json') as f:
        data = json.load(f)
    df_bestiary = pd.json_normalize(data, max_level=1)

    df_bestiary = preprocess_bestiary(df_bestiary)
    df_bestiary['chunks'], df_bestiary["embeddings"] = zip(*df_bestiary['search_desc'].map(lambda x: create_splits(x)))
    chunked_bestiary = df_bestiary.explode(['chunks', "embeddings"]).reset_index(drop=True)
    chunked_bestiary = chunked_bestiary.rename(
        columns={"Класс Доспеха": "Armor_Class", "Хиты": "HP", "Скорость": "Speed", "Навыки": "Skills",
                 "Иммунитет к урону": "Damage_Immunity",
                 "Чувства": "Senses", "Языки": "Languages", "Опасность": "Challenge_rating",
                 "Бонус мастерства": " Proficiency_Bonus", "Уязвимость к урону": "Damage_Vulnerability",
                 "Спасброски": "Saving_throws"})
    chunked_bestiary.to_csv("C:\\Users\\leftg\\PycharmProjects\\data_engineering\\data\\bestiary.csv", index=False,na_rep=" ")

    df_spells = pd.read_json("C:\\Users\\leftg\\PycharmProjects\\data_engineering\\data\\spells_parsed.json")
    df_spells = preprocess_spells(df_spells)
    df_spells["embeddings"] = df_spells["desc"].apply(lambda x: embed_fun.embed_documents(x))
    df_spells.to_csv("C:\\Users\\leftg\\PycharmProjects\\data_engineering\\data\\spells.csv",na_rep=" ")


    df_items = pd.read_json("C:\\Users\\leftg\\PycharmProjects\\data_engineering\\data\\items.json")
    df_items = preprocess_items(df_items)
    df_items['chunks'],df_items["embeddings"] = zip(*df_items['description'].map(lambda x: create_splits(x)))
    chunked_items= df_items.explode(['chunks',"embeddings"]).reset_index(drop=True)
    chunked_items.to_csv("C:\\Users\\leftg\\PycharmProjects\\data_engineering\\data\\items.csv", index=False,na_rep=" ")
    logger.info(f"Preprocessing finished.Time elapsed: {time.now() - start}")

if __name__ == "__main__":
    preprocess_all()