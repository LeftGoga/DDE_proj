# init_db_items.py

import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, select
from sqlalchemy.orm import sessionmaker, declarative_base
from pgvector.sqlalchemy import VECTOR
import ast
import random
from query import find_similar_records
# Define the database URL (replace with your own credentials)
DATABASE_URL = "postgresql+psycopg2://leftg:673091@localhost:5432/dnd"

# Create a database engine
engine = create_engine(DATABASE_URL)

# Ensure pgvector extension is enabled (run this manually if needed)
# CREATE EXTENSION IF NOT EXISTS vector;

# Define the base class for ORM
Base = declarative_base()


# Define the ItemsEmbedding model
class ItemsEmbedding(Base):
    __tablename__ = 'items_embeddings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    cost = Column(String, nullable=False)
    type = Column(String, nullable=False)
    description = Column(String, nullable=True)
    chunks = Column(String, nullable=True)
    embeddings = Column(VECTOR(312), nullable=False)  # Ensure VECTOR type


def clean_embedding(embedding_str, expected_dim=312):
    try:
        embedding = ast.literal_eval(embedding_str)
        if len(embedding) > expected_dim:
            return embedding[:expected_dim]  # Truncate
        elif len(embedding) < expected_dim:
            return embedding + [0.0] * (expected_dim - len(embedding))  # Pad
        return embedding
    except Exception:
        return [0.0] * expected_dim  # Default to zero-vector if invalid


def load_embeddings_from_csv(session, csv_path):
    """Load embeddings from a CSV file into the database."""
    df = pd.read_csv(csv_path,keep_default_na=False)
    df = df.head(10)  # Limit to 10 rows for testing
    df['embeddings'] = df['embeddings'].apply(clean_embedding)

    # Check that the CSV has the required columns
    if 'embeddings' not in df.columns:
        raise ValueError("CSV must have an 'embeddings' column.")

    for _, row in df.iterrows():
        try:
            item = ItemsEmbedding(
                name=row.get('name', ''),
                cost=row.get('cost', ''),
                type=row.get('type', ''),
                description=row.get('description', ''),
                chunks=row.get('chunks', ''),
                embeddings=row.get('embeddings', '')
            )
            session.add(item)
        except (ValueError, SyntaxError) as e:
            print(f"Error parsing embeddings for row: {row.get('name', 'Unknown')}, Error: {e}")

    session.commit()

def init_db_items(csv_path, query_embedding=None):
    """Initialize the database, load data, and find similar items."""
    # Drop and recreate the table
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Load embeddings from CSV
    load_embeddings_from_csv(session, csv_path)

    # Find similar items if a query embedding is provided
    if query_embedding:
        similar_spells = find_similar_records(session, ItemsEmbedding, query_embedding)
        for spell in similar_spells:
            print(f"Name: {spell.title}, Description: {spell.desc}")
    # Close the session
    session.close()


if __name__ == "__main__":
    # Path to the CSV file
    csv_path = "items.csv"

    # Example query embedding (replace with your actual query embedding)
    query_embedding = [random.uniform(1.5, 1.9) for _ in range(312)]

    # Initialize the database and load data
    init_db_items(csv_path, query_embedding)