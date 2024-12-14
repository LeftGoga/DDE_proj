
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, select
from sqlalchemy.orm import sessionmaker, declarative_base
from pgvector.sqlalchemy import VECTOR
import ast
from query import find_similar_records
DATABASE_URL = "postgresql+psycopg2://leftg:673091@localhost:5432/dnd"

engine = create_engine(DATABASE_URL)

Base = declarative_base()

class SpellEmbedding(Base):
    __tablename__ = 'spells_embeddings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    title_en = Column(String, nullable=True)
    link = Column(String, nullable=True)
    level = Column(String, nullable=True)
    school = Column(String, nullable=True)
    cast = Column(String, nullable=True)
    dist = Column(String, nullable=True)
    comp = Column(String, nullable=True)
    duration = Column(String, nullable=True)
    classes = Column(String, nullable=True)
    source = Column(String, nullable=True)
    desc = Column(String, nullable=True)
    embeddings = Column(VECTOR(312), nullable=False)

def clean_embedding(embedding_str, expected_dim=312):
    try:
        embedding = ast.literal_eval(embedding_str)

        if any(isinstance(i, list) for i in embedding):
            embedding = [item for sublist in embedding for item in sublist]

        if len(embedding) > expected_dim:
            return embedding[:expected_dim]
        elif len(embedding) < expected_dim:
            return embedding + [0.0] * (expected_dim - len(embedding))

        return embedding
    except Exception as e:
        print(f"Error parsing embedding: {e}")
        return [0.0] * expected_dim

def load_embeddings_from_csv(session, csv_path):
    df = pd.read_csv(csv_path,keep_default_na=False)
    df = df.head(10)

    df['embeddings'] = df['embeddings'].apply(clean_embedding)

    required_columns = ['title', 'title_en', 'link', 'level', 'school', 'cast', 'dist', 'comp', 'duration', 'classes', 'source', 'desc', 'embeddings']
    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"CSV must have a '{column}' column.")

    for _, row in df.iterrows():
        try:
            spell = SpellEmbedding(
                title=row.get('title', ''),
                title_en=row.get('title_en', ''),
                link=row.get('link', ''),
                level=row.get('level', ''),
                school=row.get('school', ''),
                cast=row.get('cast', ''),
                dist=row.get('dist', ''),
                comp=row.get('comp', ''),
                duration=row.get('duration', ''),
                classes=row.get('classes', ''),
                source=row.get('source', ''),
                desc=row.get('desc', ''),
                embeddings=row['embeddings']
            )
            session.add(spell)
        except (ValueError, SyntaxError) as e:
            print(f"Error parsing row: {row.get('title', 'Unknown')}, Error: {e}")

    session.commit()

def find_similar_spells(session, query_embedding, top_n=5):
    stmt = (
        select(SpellEmbedding)
        .order_by(SpellEmbedding.embedding.l2_distance(query_embedding))
        .limit(top_n)
    )
    results = session.scalars(stmt).all()
    return results

def init_db_spells(csv_path,query_embedding=None):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    if query_embedding:
        similar_spells = find_similar_records(session, SpellEmbedding, query_embedding)
        for spell in similar_spells:
            print(f"Name: {spell.title}, Description: {spell.desc}")
    load_embeddings_from_csv(session, csv_path)


    session.close()

if __name__ == "__main__":
    csv_path = "spells.csv"
    query_embedding = [0.1] * 312
    init_db_spells(csv_path)
