from db_bestiary import init_db_creatures
from db_spells import  init_db_spells
import random

if __name__ == "__main__":
    # Path to the CSV file
    csv_path_bestiary = "bestiary.csv"
    csv_path_spells = "spells.csv"
    # Run the initialization function
    init_db_creatures(csv_path_bestiary)
    init_db_spells(csv_path_spells, query_embedding=[random.uniform(1.5, 1.9) for x in range(312)])
