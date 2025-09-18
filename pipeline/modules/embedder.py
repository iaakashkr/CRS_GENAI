#embedder.py
import os
import numpy as np
import pandas as pd
import faiss
import pickle
import time
from rank_bm25 import BM25Okapi
from Openapi_key_store import OPENAI_API_KEY
import openai   # OpenAI API for embeddings

# ---- Flexible Embedder using OpenAI ----
class Embedder:
    def __init__(self, model_name="text-embedding-3-small", api_key=OPENAI_API_KEY):
        """
        Initialize OpenAI embedding model
        """
        self.model_name = model_name
        if api_key:
            openai.api_key = api_key
        # Otherwise, use environment variable OPENAI_API_KEY

    def embed(self, query: str):
        """
        Return normalized embedding vector as list (compatible with FAISS)
        """
        response = openai.Embedding.create(
            model=self.model_name,
            input=query
        )
        embedding = response['data'][0]['embedding']
        # normalize to unit vector (FAISS IP expects L2-normalized)
        vec = np.array(embedding, dtype="float32")
        vec /= np.linalg.norm(vec) + 1e-10
        return vec.tolist()


# ---- Embedding wrapper ----
def _embed(query, embedder):
    return embedder.embed(query)


def embedding_creation(df_summ, embedding_column_name: str, output_name: str, embedder):
    embeddings_list_chunks = []
    for index, row in df_summ.iterrows():
        Column_chunk = row[embedding_column_name]
        try:
            embeddings_chunk = _embed(Column_chunk, embedder)
            embeddings_list_chunks.append(embeddings_chunk)
        except Exception as e:
            print(f'error {e} at {index}, retrying in 10s...')
            time.sleep(10)
            embeddings_chunk = _embed(Column_chunk, embedder)
            embeddings_list_chunks.append(embeddings_chunk)

        print(f'{index} embedding created')

    # Convert to FAISS index
    dimension = len(embeddings_list_chunks[0])
    array_chunk = np.asarray(embeddings_list_chunks).astype(np.float32)
    faiss.normalize_L2(array_chunk)
    index_1 = faiss.IndexFlatIP(dimension)
    index_1.add(array_chunk)

    output = f'{output_name}.faiss'
    # ---- Ensure directory exists ----
    os.makedirs(os.path.dirname(output), exist_ok=True)
    faiss.write_index(index_1, output)
    print(f"✅ Saved FAISS index at {output}")


# ---- Sparse BM25 ----
def create_sparse_model(documents: list, bm25_model_name: str):
    tokenized_docs = [doc.split(" ") for doc in documents]
    bm25 = BM25Okapi(tokenized_docs)
    # ---- Ensure directory exists ----
    os.makedirs(os.path.dirname(bm25_model_name), exist_ok=True)
    with open(bm25_model_name, 'wb') as f:
        pickle.dump(bm25, f)
    print(f"✅ Saved BM25 model at {bm25_model_name}")


# ---- Run pipeline ----
if __name__ == "__main__":
    df_few_shots = pd.read_csv("fewshot_example.csv")
    print("Columns:", df_few_shots.columns)

    embedder = Embedder(model_name="text-embedding-3-small")  # OpenAI embeddings

    embedding_creation(df_few_shots, "question", r"embeddings/fewshot_embeddings", embedder)
    create_sparse_model(df_few_shots["question"].to_list(), r"pickles/sysntactic_model_few_shot.pkl")
