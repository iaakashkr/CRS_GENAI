# # embedder.py
# import os
# import numpy as np
# import pandas as pd
# import faiss
# import pickle
# import time
# from rank_bm25 import BM25Okapi
# from sentence_transformers import SentenceTransformer

# # ---- Flexible Embedder using Hugging Face ----
# class Embedder:
#     """
#     Drop-in replacement for OpenAI Embedder using Hugging Face SentenceTransformer.
#     Interface stays the same for embedding_creation.
#     """
#     def __init__(self, model_name="all-MiniLM-L6-v2", device=None):
#         self.model = SentenceTransformer(model_name, device=device)

#     def embed(self, query: str):
#         """
#         Return normalized embedding vector as list (compatible with FAISS)
#         """
#         emb = self.model.encode(query, convert_to_numpy=True)
#         emb = emb.astype("float32")
#         emb /= np.linalg.norm(emb) + 1e-10
#         return emb.tolist()


# # ---- Embedding wrapper ----
# def _embed(query, embedder):
#     return embedder.embed(query)


# def embedding_creation(df_summ, embedding_column_name: str, output_name: str, embedder):
#     embeddings_list_chunks = []
#     for index, row in df_summ.iterrows():
#         Column_chunk = row[embedding_column_name]
#         try:
#             embeddings_chunk = _embed(Column_chunk, embedder)
#             embeddings_list_chunks.append(embeddings_chunk)
#         except Exception as e:
#             print(f'error {e} at {index}, retrying in 10s...')
#             time.sleep(10)
#             embeddings_chunk = _embed(Column_chunk, embedder)
#             embeddings_list_chunks.append(embeddings_chunk)

#         print(f'{index} embedding created')

#     # Convert to FAISS index
#     dimension = len(embeddings_list_chunks[0])
#     array_chunk = np.asarray(embeddings_list_chunks).astype(np.float32)
#     faiss.normalize_L2(array_chunk)
#     index_1 = faiss.IndexFlatIP(dimension)
#     index_1.add(array_chunk)

#     output = f'{output_name}.faiss'
#     os.makedirs(os.path.dirname(output), exist_ok=True)
#     faiss.write_index(index_1, output)
#     print(f"✅ Saved FAISS index at {output}")


# # ---- Sparse BM25 ----
# def create_sparse_model(documents: list, bm25_model_name: str):
#     tokenized_docs = [doc.split(" ") for doc in documents]
#     bm25 = BM25Okapi(tokenized_docs)
#     os.makedirs(os.path.dirname(bm25_model_name), exist_ok=True)
#     with open(bm25_model_name, 'wb') as f:
#         pickle.dump(bm25, f)
#     print(f"✅ Saved BM25 model at {bm25_model_name}")


# # ---- Run pipeline ----
# if __name__ == "__main__":
#     df_few_shots = pd.read_csv(r"C:\Users\akash\Desktop\Projects\crs_genai\fewshot_example.csv")
#     print("Columns:", df_few_shots.columns)

#     embedder = Embedder(model_name="all-MiniLM-L6-v2")  # Hugging Face embeddings

#     embedding_creation(df_few_shots, "question", r"embeddings/fewshot_embeddings", embedder)
#     create_sparse_model(df_few_shots["question"].to_list(), r"pickles/sysntactic_model_few_shot.pkl")


# embedder.py
import os
import numpy as np
import pandas as pd
import faiss
import pickle
import time
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from pipeline.utils.cache_manager import CacheManager

cache = CacheManager()

# ---- Flexible Embedder using Hugging Face ----
class Embedder:
    """
    Drop-in replacement for OpenAI Embedder using Hugging Face SentenceTransformer.
    Interface stays the same for embedding_creation.
    """
    def __init__(self, model_name="all-MiniLM-L6-v2", device=None):
        self.model = SentenceTransformer(model_name, device=device)

    def embed(self, query: str):
        """
        Return normalized embedding vector as list (compatible with FAISS)
        """
        emb = self.model.encode(query, convert_to_numpy=True)
        emb = emb.astype("float32")
        emb /= np.linalg.norm(emb) + 1e-10
        return emb.tolist()


# ---- Embedding wrapper ----
def _embed(query, embedder):
    return embedder.embed(query)


def embedding_creation(df_summ, embedding_column_name: str, output_name: str, embedder):
    """
    Create (or load from cache) FAISS index for given DataFrame and column.
    """
    cache_key = f"faiss_{os.path.basename(output_name)}"
    cached_index = cache.load(cache_key)
    if cached_index is not None:
        print(f"✅ Loaded FAISS index from cache for {output_name}")
        return cached_index

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

    # Save FAISS to disk and cache
    output = f'{output_name}.faiss'
    os.makedirs(os.path.dirname(output), exist_ok=True)
    faiss.write_index(index_1, output)
    cache.save(cache_key, index_1)

    print(f"✅ Saved FAISS index at {output} and cached in memory.")
    return index_1


# ---- Sparse BM25 ----
def create_sparse_model(documents: list, bm25_model_name: str):
    """
    Create (or load from cache) BM25 model for given list of documents.
    """
    cache_key = f"bm25_{os.path.basename(bm25_model_name)}"
    cached_bm25 = cache.load(cache_key)
    if cached_bm25 is not None:
        print(f"✅ Loaded BM25 model from cache for {bm25_model_name}")
        return cached_bm25

    tokenized_docs = [doc.split(" ") for doc in documents]
    bm25 = BM25Okapi(tokenized_docs)
    os.makedirs(os.path.dirname(bm25_model_name), exist_ok=True)
    with open(bm25_model_name, 'wb') as f:
        pickle.dump(bm25, f)
    cache.save(cache_key, bm25)

    print(f"✅ Saved BM25 model at {bm25_model_name} and cached in memory.")
    return bm25


# ---- Run pipeline ----
if __name__ == "__main__":
    df_few_shots = pd.read_csv(r"C:\Users\akash\Desktop\Projects\crs_genai\fewshot_example.csv")
    print("Columns:", df_few_shots.columns)

    embedder = Embedder(model_name="all-MiniLM-L6-v2")  # Hugging Face embeddings

    # 🚀 Cached FAISS + BM25 creation
    embedding_creation(df_few_shots, "question", r"embeddings/fewshot_embeddings", embedder)
    create_sparse_model(df_few_shots["question"].to_list(), r"pickles/sysntactic_model_few_shot.pkl")
