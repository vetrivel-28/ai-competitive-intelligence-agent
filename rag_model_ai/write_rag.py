code = """\
\"\"\"
RAG Model
Dataset : reddit_vader_results (laptop reviews with VADER sentiment)
Flow    : User Query -> Embed -> FAISS Search -> Top-1 Result -> Answer
\"\"\"

import os
import pickle
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

CACHE_FILE = \"rag_cache.pkl\"
DATA_DIR   = \"reddit_vader_results/reddit_vader_results\"


# 1. Load Dataset
def load_dataset(data_dir):
    frames = []
    for fname in os.listdir(data_dir):
        if fname.endswith(\".csv\") and fname != \"all_reddit_cleaned.csv\":
            df = pd.read_csv(os.path.join(data_dir, fname))
            df[\"brand\"]   = fname.split(\"_\")[0]
            df[\"product\"] = fname.replace(\".csv\", \"\").replace(\"_\", \" \")
            frames.append(df)
    combined = pd.concat(frames, ignore_index=True)
    combined = combined.dropna(subset=[\"sentence\"])
    combined[\"sentence\"] = combined[\"sentence\"].astype(str).str.strip()
    return combined[combined[\"sentence\"] != \"\"].reset_index(drop=True)


# 2. Build FAISS Index
def build_index(df, embed_model):
    if os.path.exists(CACHE_FILE):
        print(\"Loading embeddings from cache ...\")
        with open(CACHE_FILE, \"rb\") as f:
            embeddings = pickle.load(f)
    else:
        print(f\"Encoding {len(df)} sentences ...\")
        embeddings = embed_model.encode(
            df[\"sentence\"].tolist(), batch_size=64,
            show_progress_bar=True, convert_to_numpy=True
        ).astype(\"float32\")
        with open(CACHE_FILE, \"wb\") as f:
            pickle.dump(embeddings, f)
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    print(f\"Index ready - {index.ntotal} vectors\")
    return index, embeddings


# 3. Retrieval — returns only the single best match
def retrieve(query, df, index, embed_model):
    q_emb = embed_model.encode([query], convert_to_numpy=True).astype(\"float32\")
    faiss.normalize_L2(q_emb)
    scores, indices = index.search(q_emb, 1)
    row = df.iloc[indices[0][0]]
    return {
        \"product\":          row[\"product\"],
        \"brand\":            row[\"brand\"],
        \"sentence\":         row[\"sentence\"],
        \"sentiment\":        row.get(\"sentiment\", \"N/A\"),
        \"compound_score\":   row.get(\"compound_score\", 0.0),
        \"similarity_score\": round(float(scores[0][0]), 4),
    }


# 4. Format Single Result
def format_result(r):
    lines = [
        \"=\" * 55,
        f\"Product         : {r['product']}\",
        f\"Brand           : {r['brand']}\",
        f\"Relevant Feature: {r['sentence']}\",
        f\"Sentiment       : {r['sentiment']} (VADER: {r['compound_score']})\",
        f\"Similarity Score: {r['similarity_score']}\",
        \"=\" * 55,
    ]
    return \"\\n\".join(lines)


# 5. Main Loop
def main():
    df = load_dataset(DATA_DIR)
    print(f\"Dataset: {len(df)} rows | {df['product'].nunique()} products\")
    embed_model = SentenceTransformer(\"all-MiniLM-L6-v2\")
    index, _ = build_index(df, embed_model)
    print(\"\\nRAG ready. Type your query (or 'quit' to exit).\\n\")
    while True:
        query = input(\"Query: \").strip()
        if not query:
            continue
        if query.lower() in {\"quit\", \"exit\", \"q\"}:
            print(\"Bye!\")
            break
        result = retrieve(query, df, index, embed_model)
        print(\"\\n\" + format_result(result) + \"\\n\")


if __name__ == \"__main__\":
    main()
"""

with open("rag_model.py", "w", encoding="utf-8") as f:
    f.write(code)

import ast
ast.parse(code)
print("rag_model.py written. Syntax OK.")
