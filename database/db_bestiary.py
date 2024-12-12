import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import VECTOR
import ast
import random
from query import find_similar_records
DATABASE_URL = "postgresql+psycopg2://leftg:673091@localhost:5432/dnd"

engine = create_engine(DATABASE_URL)

Base = declarative_base()

class CreatureEmbedding(Base):
    __tablename__ = 'creature_embeddings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    source = Column(String, nullable=True)
    abilities = Column(Text, nullable=True)
    actions = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    armor_class = Column(String, nullable=True)
    hp = Column(String, nullable=True)
    speed = Column(String, nullable=True)
    skills = Column(Text, nullable=True)
    damage_immunity = Column(String, nullable=True)
    senses = Column(String, nullable=True)
    languages = Column(String, nullable=True)
    challenge_rating = Column(String, nullable=True)
    proficiency_bonus = Column(String, nullable=True)
    saving_throws = Column(String, nullable=True)
    damage_vulnerability = Column(String, nullable=True)
    search_desc = Column(Text, nullable=True)
    chunks = Column(Text, nullable=True)
    embedding = Column(VECTOR(312), nullable=False)

def clean_embedding(embedding_str, expected_dim=312):
    try:
        embedding = ast.literal_eval(embedding_str)
        if len(embedding) > expected_dim:
            return embedding[:expected_dim]
        elif len(embedding) < expected_dim:
            return embedding + [0.0] * (expected_dim - len(embedding))
        return embedding
    except Exception:
        return [0.0] * expected_dim

def load_embeddings_from_csv(session, csv_path):
    df = pd.read_csv(csv_path)
    df = df.head(10)
    df['embeddings'] = df['embeddings'].apply(clean_embedding)
    df['Skills'] = df['Skills'].astype(str)
    df['Damage_Immunity'] = df['Damage_Immunity'].astype(str)
    df["Saving_throws"] = df["Saving_throws"].astype(str)

    if 'embeddings' not in df.columns:
        raise ValueError("CSV must have an 'embeddings' column.")

    for _, row in df.iterrows():
        try:
            creature = CreatureEmbedding(
                name=row.get('Name', ''),
                source=row.get('Source', ''),
                abilities=row.get('Abilities', ''),
                actions=row.get('Actions', ''),
                description=row.get('Description', ''),
                armor_class=row.get('Armor_Class', ''),
                hp=row.get('HP', ''),
                speed=row.get('Speed', ''),
                skills=str(row.get('Skills', '')),
                damage_immunity=row.get('Damage_Immunity', ''),
                senses=row.get('Senses', ''),
                languages=row.get('Languages', ''),
                challenge_rating=row.get('Challenge_rating', None),
                proficiency_bonus=row.get('Proficiency_Bonus', None),
                saving_throws=row.get('Saving_throws', ''),
                damage_vulnerability=row.get('Damage_Vulnerability', ''),
                search_desc=row.get('search_desc', ''),
                chunks=row.get('chunks', ''),
                embedding=row.get('embeddings', '')
            )
            session.add(creature)
        except (ValueError, SyntaxError) as e:
            print(f"Error parsing embeddings for row: {row['Name']}, Error: {e}")

    session.commit()

def find_similar_creatures(session, query_embedding, top_n=5):
    result = session.query(
        CreatureEmbedding.name,
        CreatureEmbedding.description,
        CreatureEmbedding.embedding.l2_distance(query_embedding).label('distance')
    ).order_by('distance').limit(top_n).all()

    return result

def init_db_creatures(csv_path,query_embedding=None):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    load_embeddings_from_csv(session, csv_path)
    if query_embedding:
        similar_spells = find_similar_records(session, CreatureEmbedding, query_embedding)
        for spell in similar_spells:
            print(f"Name: {spell.title}, Description: {spell.desc}")

    session.close()

if __name__ == "__main__":
    csv_path = "bestiary.csv"
    init_db_creatures(csv_path)
