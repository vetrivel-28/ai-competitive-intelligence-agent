"""Run example queries against the RAG model non-interactively."""
from rag_model import load_dataset, build_index, retrieve, format_results, DATA_DIR
from sentence_transformers import SentenceTransformer

df = load_dataset(DATA_DIR)
model = SentenceTransformer("all-MiniLM-L6-v2")
index, _ = build_index(df, model)

queries = [
    "best gaming laptop with good performance",
    "laptop with long battery life",
    "budget laptop for students",
    "laptop overheating issues",
    "best display quality laptop",
]

for query in queries:
    print(f"\n{'='*60}")
    print(f"QUERY: {query}")
    print('='*60)
    results = retrieve(query, df, index, model, top_k=3)
    print(format_results(results))
