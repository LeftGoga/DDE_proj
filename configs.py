from dotenv import load_dotenv
import os
load_dotenv(".env")
DB_PATH = os.getenv("DB_PATH")
CSV_PATHS = {
    "bestiary": "../data/bestiary.csv",
    "spells": "../data/spells.csv",
    "rules": "../data/rules.csv",
    "items": "../data/items.csv",
}
model_name = "DeepPavlov/rubert-base-cased"