"""
RAG (Retrieval-Augmented Generation) Engine
Uses local sentence transformers + FAISS for semantic search over analysis data
"""

import pandas as pd
import numpy as np
import os
import pickle
from sentence_transformers import SentenceTransformer
import faiss

# ── Build knowledge base from all CSV/TXT files ──────────────────────────────

def load_documents():
    """Load all analysis data into text chunks"""
    docs = []

    # CSV files → row-level chunks
    csv_files = {
        'competitor_analysis.csv':          'competitor pricing and ratings',
        'brand_sentiment_analysis.csv':     'brand sentiment analysis',
        'positive_keywords.csv':            'positive customer feedback keywords',
        'negative_keywords.csv':            'negative customer complaints keywords',
        'market_opportunities_detected.csv':'market opportunity trends',
        'competitive_strategies.csv':       'competitive strategy recommendations',
        'opportunity_insights.csv':         'opportunity insights and details',
        'amazon.csv':                       'Amazon product data',
        'flipkart.csv':                     'Flipkart product data',
        'reddit.csv':                       'Reddit user discussions',
        'youtube.csv':                      'YouTube comment discussions',
    }

    for filename, description in csv_files.items():
        if not os.path.exists(filename):
            continue
        try:
            df = pd.read_csv(filename)
            for _, row in df.iterrows():
                text = f"[{description}] " + " | ".join(
                    f"{col}: {val}"
                    for col, val in row.items()
                    if pd.notna(val) and str(val).strip() not in ('', 'N/A', 'nan')
                )
                if len(text) > 30:
                    docs.append(text)
        except Exception as e:
            print(f"   ⚠️ Could not load {filename}: {e}")

    # Text report files → paragraph-level chunks
    txt_files = [
        'competitor_analysis_report.txt',
        'market_insights_report.txt',
        'competitive_strategies_report.txt',
        'opportunity_detection_report.txt',
    ]

    for filename in txt_files:
        if not os.path.exists(filename):
            continue
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            # Split into ~300-char chunks on double newlines
            paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 40]
            docs.extend(paragraphs)
        except Exception as e:
            print(f"   ⚠️ Could not load {filename}: {e}")

    return docs


def build_index(docs, model, index_path='rag_index.faiss', docs_path='rag_docs.pkl'):
    """Encode documents and build FAISS index"""
    print(f"   🔢 Encoding {len(docs)} documents...")
    embeddings = model.encode(docs, show_progress_bar=False, batch_size=32)
    embeddings = np.array(embeddings, dtype='float32')
    faiss.normalize_L2(embeddings)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)   # Inner-product = cosine after L2 norm
    index.add(embeddings)

    faiss.write_index(index, index_path)
    with open(docs_path, 'wb') as f:
        pickle.dump(docs, f)

    print(f"   ✅ Index built with {index.ntotal} vectors (dim={dim})")
    return index, docs


def load_or_build(model, index_path='rag_index.faiss', docs_path='rag_docs.pkl'):
    """Load cached index or rebuild if stale"""
    if os.path.exists(index_path) and os.path.exists(docs_path):
        index = faiss.read_index(index_path)
        with open(docs_path, 'rb') as f:
            docs = pickle.load(f)
        print(f"   ✅ Loaded cached index ({index.ntotal} vectors)")
        return index, docs

    docs = load_documents()
    if not docs:
        raise ValueError("No documents found. Run analysis steps 1-7 first.")
    return build_index(docs, model, index_path, docs_path)


# ── Retrieval ─────────────────────────────────────────────────────────────────

def retrieve(query, model, index, docs, top_k=6):
    """Return top-k most relevant document chunks for a query"""
    q_emb = model.encode([query], show_progress_bar=False)
    q_emb = np.array(q_emb, dtype='float32')
    faiss.normalize_L2(q_emb)

    scores, indices = index.search(q_emb, top_k)
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < len(docs):
            results.append({'text': docs[idx], 'score': float(score)})
    return results


# ── Generation (template-based LLM-free) ─────────────────────────────────────

def generate_answer(query, retrieved_chunks):
    """
    Produce a coherent answer from retrieved chunks without an external LLM.
    Uses keyword matching + structured templates for common question types.
    """
    query_lower = query.lower()
    context = "\n".join(c['text'] for c in retrieved_chunks)
    context_lower = context.lower()

    # ── Helper: extract numeric value after a label ───────────────────────
    def extract_after(label, text, default='N/A'):
        idx = text.lower().find(label.lower())
        if idx == -1:
            return default
        snippet = text[idx + len(label):idx + len(label) + 30].strip()
        token = snippet.split()[0].rstrip('|,') if snippet.split() else default
        return token

    # ── Route by question intent ──────────────────────────────────────────

    # Best / worst brand questions
    if any(w in query_lower for w in ['best', 'top', 'highest', 'most']):
        if 'price' in query_lower or 'expensive' in query_lower:
            return _answer_from_context(
                "Most Expensive Brand", context, retrieved_chunks,
                "Based on competitor analysis, the most expensive brand is identified "
                "from the average price data across Amazon and Flipkart products."
            )
        if 'rating' in query_lower or 'rated' in query_lower:
            return _answer_from_context(
                "Best Rated", context, retrieved_chunks,
                "Based on customer ratings across Amazon and Flipkart, "
                "the best-rated brand is determined from average rating scores."
            )
        if 'value' in query_lower:
            return _answer_from_context(
                "Value_Score", context, retrieved_chunks,
                "The best value brand is calculated using a rating-to-price ratio "
                "across all products in the dataset."
            )
        if 'battery' in query_lower:
            return _answer_from_context(
                "battery", context, retrieved_chunks,
                "Battery life feedback is extracted from customer reviews and discussions."
            )

    # Complaint / issue questions
    if any(w in query_lower for w in ['complaint', 'issue', 'problem', 'bad', 'negative', 'worst']):
        lines = [c['text'] for c in retrieved_chunks if 'negative' in c['text'].lower()
                 or 'complaint' in c['text'].lower() or 'keyword' in c['text'].lower()]
        if lines:
            answer = "**Top Customer Complaints & Issues:**\n\n"
            for line in lines[:4]:
                answer += f"• {line[:200]}\n\n"
            return answer
        return _fallback(retrieved_chunks)

    # Strategy questions
    if any(w in query_lower for w in ['strategy', 'recommend', 'suggest', 'should', 'improve']):
        brand = _detect_brand(query_lower)
        lines = [c['text'] for c in retrieved_chunks
                 if 'strategy' in c['text'].lower() or 'keyword' in c['text'].lower()]
        if lines:
            answer = f"**Strategy Recommendations{' for ' + brand.title() if brand else ''}:**\n\n"
            for line in lines[:4]:
                answer += f"• {line[:250]}\n\n"
            return answer
        return _fallback(retrieved_chunks)

    # Sentiment questions
    if any(w in query_lower for w in ['sentiment', 'positive', 'opinion', 'feel', 'customer']):
        brand = _detect_brand(query_lower)
        lines = [c['text'] for c in retrieved_chunks if 'sentiment' in c['text'].lower()]
        if lines:
            answer = f"**Sentiment Analysis{' for ' + brand.title() if brand else ''}:**\n\n"
            for line in lines[:4]:
                answer += f"• {line[:250]}\n\n"
            return answer
        return _fallback(retrieved_chunks)

    # Opportunity / trend questions
    if any(w in query_lower for w in ['opportunit', 'trend', 'growing', 'emerging', 'market']):
        lines = [c['text'] for c in retrieved_chunks
                 if 'opportunit' in c['text'].lower() or 'mention' in c['text'].lower()]
        if lines:
            answer = "**Market Opportunities & Trends:**\n\n"
            for line in lines[:5]:
                answer += f"• {line[:250]}\n\n"
            return answer
        return _fallback(retrieved_chunks)

    # Price questions
    if any(w in query_lower for w in ['price', 'cost', 'cheap', 'afford', 'budget']):
        lines = [c['text'] for c in retrieved_chunks
                 if 'price' in c['text'].lower() or 'avg_price' in c['text'].lower()]
        if lines:
            answer = "**Price Analysis:**\n\n"
            for line in lines[:4]:
                answer += f"• {line[:250]}\n\n"
            return answer
        return _fallback(retrieved_chunks)

    # Generic fallback — just surface the top chunks
    return _fallback(retrieved_chunks)


def _detect_brand(text):
    brands = ['dell', 'hp', 'lenovo', 'asus', 'acer', 'msi', 'apple', 'samsung']
    for b in brands:
        if b in text:
            return b
    return ''


def _answer_from_context(keyword, context, chunks, default_intro):
    lines = [c['text'] for c in chunks if keyword.lower() in c['text'].lower()]
    if lines:
        answer = f"**{default_intro}**\n\n"
        for line in lines[:4]:
            answer += f"• {line[:250]}\n\n"
        return answer
    return _fallback(chunks)


def _fallback(chunks):
    answer = "**Based on the analysis data:**\n\n"
    for chunk in chunks[:4]:
        answer += f"• {chunk['text'][:250]}\n\n"
    return answer


# ── Public API ────────────────────────────────────────────────────────────────

_model = None
_index = None
_docs  = None

def get_rag_components():
    """Lazy-load model + index (cached across Streamlit reruns via module globals)"""
    global _model, _index, _docs
    if _model is None:
        print("   🤖 Loading sentence transformer model...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    if _index is None:
        _index, _docs = load_or_build(_model)
    return _model, _index, _docs


def ask(question):
    """Main entry point: question → answer string"""
    model, index, docs = get_rag_components()
    chunks = retrieve(question, model, index, docs, top_k=6)
    return generate_answer(question, chunks), chunks


def rebuild_index():
    """Force rebuild the index (call after new analysis runs)"""
    global _index, _docs
    for f in ('rag_index.faiss', 'rag_docs.pkl'):
        if os.path.exists(f):
            os.remove(f)
    _index, _docs = None, None
    model, index, docs = get_rag_components()
    return index.ntotal


if __name__ == '__main__':
    print("=" * 60)
    print("RAG ENGINE - SELF TEST")
    print("=" * 60)
    test_questions = [
        "Which brand has the best rating?",
        "What are the top customer complaints?",
        "What strategy should HP follow?",
        "Which laptop segment is growing fastest?",
        "What do customers say about battery life?",
    ]
    for q in test_questions:
        print(f"\n❓ {q}")
        answer, _ = ask(q)
        print(f"💬 {answer[:300]}...")
        print("-" * 60)
