import json
from loguru import logger
from parsing.items import get_items
from parsing.mechanics import get_mechanics
from parsing.spells import get_spells
from parsing.dop_info import get_dop_info
from parsing.bestiary import get_monsters

# Configure Loguru to output logs to the console only
logger.remove()  # Remove default handler
logger.add(
    sink=lambda msg: print(msg, end=''),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO",
)

def parse_all():
    parse_functions = [get_dop_info, get_spells, get_mechanics, get_items, get_monsters]
    file_names = ["basics", "spells_parsed", "mechanics", "items", "bestiary"]
    for index, parse_function in enumerate(parse_functions):
        try:
            result = parse_function()
            file_name = f"{file_names[index]}.json"
            file_path = f"C:\\Users\\leftg\\PycharmProjects\\data_engineering\\data\\{file_name}"
            with open(file_path, 'w', encoding='utf-8') as json_file:
                logger.info(f"Creating {file_name}")
                json.dump(result, json_file, ensure_ascii=False, indent=2)
            logger.success(f"Saved: {file_name}")
        except Exception as e:
            logger.error(f"Failed to process {file_names[index]}: {e}")

if __name__ == "__main__":
    parse_all()
