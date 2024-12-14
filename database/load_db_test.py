import random
from database.db_items import init_db_items, find_similar_records as find_similar_items
from database.db_mechanics import init_db_rules, find_similar_records as find_similar_rules
from db_bestiary import init_db_creatures, find_similar_records as find_similar_creatures
from db_spells import init_db_spells, find_similar_records as find_similar_spells
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from update_db import update_database
import random
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.db_items import ItemsEmbedding
from database.db_mechanics import RulesEmbedding as RulesEmbedding
from db_bestiary import CreatureEmbedding as CreatyreEmbedding
from db_spells import SpellEmbedding
from query import find_similar_records  # Import the generic querying function

# Configuration for database URL and CSV paths
DATABASE_URL = "postgresql+psycopg2://leftg:673091@localhost:5432/dnd"
CSV_PATHS = {
    "bestiary": "./data/bestiary.csv",
    "spells": "./data/spells.csv",
    "rules": "./data/rules.csv",
    "items": "./data/main.csv",
    "update":"./data/update.csv"
}

# Create a database engine
engine = create_engine(DATABASE_URL)

def generate_query_embedding():
    """Generate a random query embedding."""
    return [random.uniform(1.5, 1.9) for _ in range(312)]

def initialize_databases():
    """Initialize all databases."""
    try:
        print("Initializing bestiary database...")
        init_db_creatures(CSV_PATHS["bestiary"])
        print("Bestiary database initialized successfully.\n")

        print("Initializing spells database...")
        init_db_spells(CSV_PATHS["spells"])
        print("Spells database initialized successfully.\n")

        print("Initializing rules database...")
        init_db_rules(CSV_PATHS["rules"])
        print("Rules database initialized successfully.\n")

        print("Initializing items database...")
        init_db_items(CSV_PATHS["items"])
        print("Items database initialized successfully.\n")

    except Exception as e:
        print(f"An error occurred during database initialization: {e}")

def query_databases():
    """Query all databases for similar records."""

    Session = sessionmaker(bind=engine)
    session = Session()

    try:

        print("Querying bestiary database...")
        query_embedding = generate_query_embedding()
        similar_creatures = find_similar_records(session, CreatyreEmbedding, query_embedding, top_n=5)
        for creature in similar_creatures:
            print(f"Bestiary: Name: {creature.name}, Description: {creature.description}")
        print("Bestiary database queried successfully.\n")


        print("Querying spells database...")
        query_embedding = generate_query_embedding()
        similar_spells = find_similar_records(session, SpellEmbedding, query_embedding, top_n=5)
        for spell in similar_spells:
            print(f"Spells: Name: {spell.title}, Description: {spell.desc}")
        print("Spells database queried successfully.\n")


        print("Querying rules database...")
        query_embedding = generate_query_embedding()
        similar_rules = find_similar_records(session, RulesEmbedding, query_embedding, top_n=5)
        for rule in similar_rules:
            print(f"Rules: Name: {rule.name}, Description: {rule.description}")
        print("Rules database queried successfully.\n")


        print("Querying items database...")
        query_embedding = generate_query_embedding()
        similar_items = find_similar_records(session, ItemsEmbedding, query_embedding, top_n=5)
        for item in similar_items:
            print(f"Items: Name: {item.name}, Description: {item.description}")
        print("Items database queried successfully.\n")

    except Exception as e:
        print(f"An error occurred during database querying: {e}")
    finally:
        # Close the session
        session.close()

def update_items():
    """Update the items database."""
    print("Updating items database...")

    update_database(engine, ItemsEmbedding, CSV_PATHS["update"])

if __name__ == "__main__":
    # Initialize all database
    initialize_databases()

    # Query all databases
    query_databases()
    update_items()
    query_databases()