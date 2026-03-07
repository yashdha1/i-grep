import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
 
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2" 
LOCAL_MODEL_FOLDER = "all-MiniLM-L6-v2"
LOCAL_MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models")
LOCAL_MODEL_PATH = os.path.join(LOCAL_MODELS_DIR, LOCAL_MODEL_FOLDER)

_model = None


def _is_model_present(path: str) -> bool: 
    return os.path.isfile(os.path.join(path, "config.json"))

def get_model_path() -> str: 
    return LOCAL_MODEL_PATH

def download_and_save_model_locally() -> None: 
    if _is_model_present(LOCAL_MODEL_PATH):
        return
    os.makedirs(os.path.dirname(LOCAL_MODEL_PATH), exist_ok=True)
    model = SentenceTransformer(MODEL_NAME)
    model.save(LOCAL_MODEL_PATH)

def _get_model(): 
    global _model

    # if models is absent download and return.
    if _model is None:
        if _is_model_present(LOCAL_MODEL_PATH):
            _model = SentenceTransformer(LOCAL_MODEL_PATH, local_files_only=True)
        else:
            download_and_save_model_locally()
            _model = SentenceTransformer(LOCAL_MODEL_PATH, local_files_only=True)

    return _model

def encode_text(text):
    return _get_model().encode(text)

def _embedding_from_db(value): 
    if value is None or value == b"" or value == "":
        return None
    try:
        if isinstance(value, bytes):
            return np.frombuffer(value, dtype=np.float32).copy()
        s = value if isinstance(value, str) else value.decode("utf-8")
        if s.strip().startswith("["):
            return np.array(json.loads(s), dtype=np.float32)
        return None
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


def search_embeddings(query, rows, top_k=5): 
    if not rows:
        return []
    query_vector = _get_model().encode([query])

    valid = []
    for row in rows:
        raw = row.embeddings
        if not raw:
            continue
        vec = _embedding_from_db(raw)
        if vec is not None:
            valid.append((row, vec))
    if not valid:
        return []

    embed_matrix = np.stack([v for _, v in valid])

    rows_only = [r for r, _ in valid] 

    embed_matrix = embed_matrix / np.linalg.norm(embed_matrix, axis=1, keepdims=True)

    query_norm = query_vector / np.linalg.norm(query_vector)

    scores = np.dot(embed_matrix, query_norm.T).flatten()

    top_indices = np.argsort(scores)[::-1][:top_k]

    return [(float(scores[i]), rows_only[i]) for i in top_indices]
