import json
from items import get_items
from mechanics import get_mechanics
from spells import get_spells
from dop_info import get_dop_info
from bestiary import get_monsters


def main():
    parse_functions = [get_dop_info,get_spells,get_mechanics,get_items],get_monsters()
    file_names = [ "basics","spells_parsed","mechanics","items","bestiary"]
    for index, parse_function in enumerate(parse_functions):
        result = parse_function()
        file_name = f"{file_names[index]}.json"
        with open("./data/"+file_name, 'w', encoding='utf-8') as json_file:
            print(f"creating {file_name}")
            json.dump(result, json_file, ensure_ascii=False, indent=2)
        print(f"Saved: {file_name}")


if __name__ == "__main__":
    main()