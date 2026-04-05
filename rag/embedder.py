# rag/embedder.py
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import hashlib

MODEL_NAME = "tfidf-simple"
_vectorizer = None


def get_vectorizer():
    global _vectorizer
    if _vectorizer is None:
        print(f"Initializing TF-IDF vectorizer: {MODEL_NAME}")
        _vectorizer = TfidfVectorizer(max_features=384, stop_words='english')
        # Fit on some dummy data to initialize
        _vectorizer.fit(["dummy text for initialization"])
    return _vectorizer


def embed_texts(texts: list[str]) -> np.ndarray:
    if not texts:
        return np.array([]).reshape(0, 384)

    vectorizer = get_vectorizer()

    # If this is the first real usage, we need to fit on the actual texts
    if len(vectorizer.get_feature_names_out()) == 1 and vectorizer.get_feature_names_out()[0] == "dummy":
        vectorizer.fit(texts)

    embeddings = vectorizer.transform(texts).toarray()

    # Ensure consistent dimensionality
    if embeddings.shape[1] < 384:
        padding = np.zeros((embeddings.shape[0], 384 - embeddings.shape[1]))
        embeddings = np.hstack([embeddings, padding])
    elif embeddings.shape[1] > 384:
        embeddings = embeddings[:, :384]

    return embeddings


def embed_query(query: str) -> np.ndarray:
    return embed_texts([query])
