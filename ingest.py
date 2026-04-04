# ingest.py
# Run this ONCE locally to build the FAISS index.
# Then commit the faiss_index/ folder to GitHub — Railway will serve it.
#
# Usage: python ingest.py
#
# Add documents to documents/ before running:
#   PIPEDA.pdf         → https://laws-lois.justice.gc.ca/PDF/P-8.6.pdf
#   OSFI_E23.txt       → https://www.osfi-bsif.gc.ca (copy page text)
#   Bill_C27_AIDA.txt  → https://www.parl.ca (copy Part 3 text)
#   CIBC_AI.txt        → https://www.cibc.com/en/about-cibc/future-banking/ai.html

import os
import json
import faiss
import numpy as np
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag.embedder import embed_texts

DOCUMENTS_DIR    = "documents"
FAISS_INDEX_DIR  = "faiss_index"
FAISS_INDEX_PATH = f"{FAISS_INDEX_DIR}/index.faiss"
CHUNKS_PATH      = f"{FAISS_INDEX_DIR}/chunks.json"
CHUNK_SIZE       = 500
CHUNK_OVERLAP    = 50


def load_documents():
    path  = Path(DOCUMENTS_DIR)
    files = list(path.glob("**/*.pdf")) + list(path.glob("**/*.txt"))
    files = [f for f in files if f.name != "README_documents.md"]

    if not files:
        raise ValueError(f"No PDF or TXT files in '{DOCUMENTS_DIR}'. Add documents first.")

    raw_docs = []
    for fp in files:
        print(f"  Loading: {fp.name}")
        try:
            loader = PyPDFLoader(str(fp)) if fp.suffix == ".pdf" else TextLoader(str(fp), encoding="utf-8")
            for page in loader.load():
                raw_docs.append({
                    "text":   page.page_content,
                    "source": fp.stem,
                    "page":   page.metadata.get("page", "N/A"),
                })
        except Exception as e:
            print(f"  ⚠️  Could not load {fp.name}: {e}")

    print(f"✓ Loaded {len(raw_docs)} pages from {len(files)} file(s)")
    return raw_docs


def chunk_documents(raw_docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = []
    for doc in raw_docs:
        if not doc["text"].strip():
            continue
        for i, text in enumerate(splitter.split_text(doc["text"])):
            if text.strip():
                chunks.append({
                    "text": text.strip(),
                    "metadata": {
                        "source":  doc["source"],
                        "page":    doc["page"],
                        "section": f"Chunk {i+1}",
                    }
                })
    avg = sum(len(c["text"]) for c in chunks) // len(chunks) if chunks else 0
    print(f"✓ Created {len(chunks)} chunks (avg {avg} chars)")
    return chunks


def build_index(chunks):
    os.makedirs(FAISS_INDEX_DIR, exist_ok=True)
    print(f"Embedding {len(chunks)} chunks...")
    embeddings = embed_texts([c["text"] for c in chunks]).astype("float32")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"✓ FAISS index saved ({index.ntotal} vectors)")


def verify():
    from rag.retriever import retrieve
    q = "What are consent requirements under PIPEDA?"
    print(f"\nVerification: '{q}'")
    results = retrieve(q)
    if results:
        for r in results:
            print(f"  [{r['source']} — {r['section']}] similarity={r['similarity_score']:.3f}")
    else:
        print("  ⚠️  No results — check your documents.")


if __name__ == "__main__":
    print("=" * 55)
    print("ComplianceNav AI — Ingestion Pipeline")
    print("=" * 55)
    print("\n1. Loading documents...")
    docs   = load_documents()
    print("\n2. Chunking...")
    chunks = chunk_documents(docs)
    print("\n3. Building FAISS index...")
    build_index(chunks)
    print("\n4. Verifying...")
    verify()
    print("\n" + "=" * 55)
    print("✅ Done. Commit faiss_index/ to GitHub, then deploy to Railway.")
    print("=" * 55)
