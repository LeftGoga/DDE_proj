import sys
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd
import streamlit as st
import numpy as np
import re
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(dotenv_path)

from configs import DB_PATH


connection_string = DB_PATH
engine = create_engine(connection_string)
pd.set_option('display.max_columns', None)

def fetch_data_with_sqlalchemy(query):
    with engine.connect() as connection:
        return pd.read_sql_query(query, connection)

def main():
    st.title("Database Dashboard")


    table_name = st.sidebar.selectbox(
        "Select a table",
        ["creature_embeddings", "items_embeddings", "rules_embeddings", "spells_embeddings"]
    )


    if table_name:
        query = f"SELECT * FROM {table_name}"
        try:
            data = fetch_data_with_sqlalchemy(query)


            data.replace("", np.nan, inplace=True)


            st.write(f"First 5 rows of `{table_name}`:")
            st.dataframe(data.head(5), use_container_width=True)


            st.write(f"Null statistics for `{table_name}`:")
            missing_values = data.isnull().sum()
            missing_values_df = (
                missing_values.to_frame(name="Null Values")
                .reset_index()
                .rename(columns={"index": "Column"})
            )
            st.dataframe(missing_values_df, use_container_width=True)


            data['vector_column'] = data['embeddings'].apply(eval)

            mean_vector = np.mean(np.stack(data['vector_column']), axis=0)


            cosine_similarities = [cosine_similarity([v], [mean_vector])[0][0] for v in data['vector_column']]
            average_cosine_similarity = np.mean(cosine_similarities)

            st.metric("Average Cosine Similarity", f"{average_cosine_similarity:.2f}")

            vector_matrix = np.stack(data['vector_column'])
            cosine_distances = []
            for i in range(len(vector_matrix)):
                for j in range(i + 1, len(vector_matrix)):
                    distance = 1 - cosine_similarity([vector_matrix[i]], [vector_matrix[j]])[0][0]
                    cosine_distances.append(distance)


            cosine_distance_variance = np.var(cosine_distances)
            st.metric("Variance of Cosine Distances", f"{cosine_distance_variance:.2f}")
            if table_name == "creature_embeddings" and 'abilities' in data.columns:
                data['abilities'] = data['abilities'].apply(eval)  # Convert string to list
                mean_abilities_length = np.mean(data['abilities'].apply(len))
                st.metric("Mean Length of Abilities", f"{mean_abilities_length:.2f}")
            elif table_name == "items_embeddings" and 'cost' in data.columns:
                data['cost'] = data['cost'].apply(eval)

                data['mean_cost'] = data['cost'].apply(lambda x: np.mean(x))

                overall_mean_cost = np.mean(data['mean_cost'])
                st.metric("Mean Cost of Items", f"{overall_mean_cost:.2f}")

            elif table_name == "rules_embeddings" and 'chunks' in data.columns:

                    data['num_sentences'] = data['chunks'].apply(
                        lambda x: len(re.split(r'(?<=[.!?]) +', x))
                    )

                    mean_num_sentences = np.mean(data['num_sentences'])
                    st.metric("Mean Number of Sentences per Chunk", f"{mean_num_sentences:.2f}")
            elif table_name == "spells_embeddings":
                st.write("### Number of Spells by School")
                school_counts = data['school'].value_counts()


                fig, ax = plt.subplots()
                school_counts.plot(kind='bar', color=plt.cm.tab20.colors, ax=ax)
                ax.set_xlabel("School")
                ax.set_ylabel("Number of Spells")
                ax.set_title("Number of Spells by School")
                ax.legend(title="School", bbox_to_anchor=(1.05, 1), loc='upper left')
                st.pyplot(fig)


                st.write("### Number of Spells by Level")
                level_counts = data['level'].value_counts().sort_index()


                fig, ax = plt.subplots()
                level_counts.plot(kind='bar', color=plt.cm.tab20.colors, ax=ax)
                ax.set_xlabel("Level")
                ax.set_ylabel("Number of Spells")
                ax.set_title("Number of Spells by Level")
                ax.legend(title="Level", bbox_to_anchor=(1.05, 1), loc='upper left')
                st.pyplot(fig)


        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()