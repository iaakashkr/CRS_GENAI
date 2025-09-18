# test_fewshot_pipeline.py
import pickle
import os
import pandas as pd
import faiss
from pipeline.modules.fewshot_module import fetch_few_shots
from pipeline.modules.embedder import Embedder  # Your unified embedder
from Openapi_key_store import OPENAI_API_KEY  # Your API key

# ---- Initialize precomputed few-shot resources ----
def init_fewshot_precomputed(
    faiss_file="embeddings/fewshot_embeddings.faiss",
    bm25_file="pickles/sysntactic_model_few_shot.pkl",
    examples_file="fewshot_example.csv"
):
    """
    Load FAISS index, BM25 model, and example dataframe
    """
    # Load examples dataframe
    examples_df = pd.read_csv(examples_file)

    # Load FAISS index
    dimension = 1536  # Correct dimension for text-embedding-3-small
    if os.path.exists(faiss_file):
        faiss_index = faiss.read_index(faiss_file)
    else:
        print(f"⚠️ FAISS file not found at {faiss_file}")
        faiss_index = faiss.IndexFlatIP(dimension)

    # Load BM25
    if os.path.exists(bm25_file):
        with open(bm25_file, "rb") as f:
            bm25_model = pickle.load(f)
        tokenized_corpus = [q.split() for q in examples_df["question"]]
    else:
        print(f"⚠️ BM25 pickle not found at {bm25_file}")
        bm25_model = None
        tokenized_corpus = None

    # Initialize OpenAI Embedder
    embedder = Embedder(model_name="text-embedding-3-small", api_key=OPENAI_API_KEY)

    return {
        "examples_df": examples_df,
        "faiss_index": faiss_index,
        "bm25_model": bm25_model,
        "tokenized_corpus": tokenized_corpus,
        "embedder": embedder
    }

# ---- Load precomputed resources ----
fewshot_resources = init_fewshot_precomputed()

faiss_index = fewshot_resources["faiss_index"]
examples_df = fewshot_resources["examples_df"]
embedder = fewshot_resources["embedder"]
bm25_model = fewshot_resources["bm25_model"]
tokenized_corpus = fewshot_resources["tokenized_corpus"]

# ---- Test function ----
def test_few_shot(user_question):
    result = fetch_few_shots(
        user_question=user_question,
        faiss_index=faiss_index,
        examples_df=examples_df.copy(),
        embedder=embedder,
        bm25_model=bm25_model,
        tokenized_corpus=tokenized_corpus,
        top_k=1
    )

    print("\n🔹 Similarity Found:", result["similarity_flag"])
    print("🔹 Matched Indices:", result.get("matched_indices", []))
    print("🔹 Top Few-Shot Examples:")
    for k, v in result["few_shot_examples"].items():
        print(f"   {k}: {v}")

# ---- CLI loop ----
if __name__ == "__main__":
    while True:
        question = input("\nEnter your question (or 'exit' to quit): ")
        if question.lower() == "exit":
            break
        test_few_shot(question)
