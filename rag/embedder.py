# rag/embedder.py
# Uses fastembed — lightweight embedder, no PyTorch dependency
# Same 384-dimension output as all-MiniLM-L6-v2, Railway-compatible

from fastembed import TextEmbedding
import numpy as np

MODEL_NAME = "BAAI/bge-small-en-v1.5"
_model = None


def get_model() -> TextEmbedding:
    global _model
    if _model is None:
        print(f"Loading embedding model: {MODEL_NAME}")
        _model = TextEmbedding(model_name=MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    model = get_model()
    embeddings = list(model.embed(texts))
    return np.array(embeddings, dtype=np.float32)


def embed_query(query: str) -> np.ndarray:
    return embed_texts([query])