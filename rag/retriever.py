# rag/retriever.py
import os
import json
import faiss
import numpy as np
from rag.embedder import embed_query

FAISS_INDEX_PATH  = "faiss_index/index.faiss"
CHUNKS_PATH       = "faiss_index/chunks.json"
MIN_SIMILARITY    = 0.35
TOP_K             = 4

_index  = None
_chunks = None


def _load_index():
    global _index, _chunks
    if not os.path.exists(FAISS_INDEX_PATH):
        raise FileNotFoundError(
            f"FAISS index not found at '{FAISS_INDEX_PATH}'. "
            "Run ingest.py locally first, then commit the faiss_index/ folder."
        )
    if _index is None:
        print("Loading FAISS index...")
        _index = faiss.read_index(FAISS_INDEX_PATH)
    if _chunks is None:
        with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
            _chunks = json.load(f)
    return _index, _chunks


def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    index, chunks = _load_index()
    query_embedding = embed_query(query).astype("float32")
    distances, indices = index.search(query_embedding, k)

    results = []
    seen = set()

    for dist, idx in zip(distances[0], indices[0]):
        if idx == -1:
            continue
        chunk = chunks[idx]
        text  = chunk["text"]
        if text in seen:
            continue
        seen.add(text)

        similarity = float(1.0 / (1.0 + dist))
        if similarity < MIN_SIMILARITY:
            continue

        results.append({
            "text":             text,
            "source":           chunk["metadata"].get("source", "Unknown"),
            "section":          chunk["metadata"].get("section", "N/A"),
            "page":             chunk["metadata"].get("page",    "N/A"),
            "similarity_score": round(similarity, 4),
        })

    return results


def build_context(chunks: list[dict]) -> str:
    if not chunks:
        return "No relevant content found in the regulatory document corpus."
    parts = []
    for i, c in enumerate(chunks, 1):
        parts.append(f"[SOURCE {i}: {c['source']} — {c['section']}]\n{c['text']}")
    return "\n\n---\n\n".join(parts)
