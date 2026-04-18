import json
import urllib.request
from pathlib import Path

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

from src.lib.dirs import cache_dir

# ---------------------------------------------------------------------------
# Model paths (stored in user cache dir, never inside site-packages)
# ---------------------------------------------------------------------------
_MODEL_DIR_NAME = "all-MiniLM-L6-v2"
_HF_BASE = "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main"

_FILES_TO_DOWNLOAD = [
    "onnx/model.onnx",
    "tokenizer.json",
    "tokenizer_config.json",
]


def _model_dir() -> Path:
    return cache_dir() / "models" / _MODEL_DIR_NAME


def get_model_path() -> str:
    return str(_model_dir())


def _is_model_present() -> bool:
    d = _model_dir()
    return (d / "onnx" / "model.onnx").is_file() and (d / "tokenizer.json").is_file()


def download_and_save_model_locally() -> None:
    if _is_model_present():
        return
    base = _model_dir()
    print(f"Downloading ONNX model to {base} ...")
    for rel in _FILES_TO_DOWNLOAD:
        dest = base / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.is_file():
            url = f"{_HF_BASE}/{rel}"
            print(f"  {rel} ...", end=" ", flush=True)
            urllib.request.urlretrieve(url, dest)
            print("done")
    print("Model ready.")


# ---------------------------------------------------------------------------
# Lazy-loaded inference session
# ---------------------------------------------------------------------------
_session: ort.InferenceSession | None = None
_tokenizer: Tokenizer | None = None


def _get_model() -> tuple[ort.InferenceSession, Tokenizer]:
    global _session, _tokenizer
    if _session is None:
        if not _is_model_present():
            download_and_save_model_locally()
        base = _model_dir()
        _session = ort.InferenceSession(
            str(base / "onnx" / "model.onnx"),
            providers=["CPUExecutionProvider"],
        )
        _tokenizer = Tokenizer.from_file(str(base / "tokenizer.json"))
        _tokenizer.enable_padding(pad_id=0, pad_token="[PAD]")
        _tokenizer.enable_truncation(max_length=256)
    return _session, _tokenizer


def _run_inference(texts: list[str]) -> np.ndarray:
    session, tokenizer = _get_model()
    encoded = tokenizer.encode_batch(texts)
    input_ids = np.array([e.ids for e in encoded], dtype=np.int64)
    attention_mask = np.array([e.attention_mask for e in encoded], dtype=np.int64)
    token_type_ids = np.zeros_like(input_ids)
    outputs = session.run(
        None,
        {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "token_type_ids": token_type_ids,
        },
    )
    # Mean pooling over token dimension, then L2-normalize
    token_embs = outputs[0]  # (batch, seq_len, 384)
    mask = attention_mask[..., np.newaxis].astype(np.float32)
    pooled = (token_embs * mask).sum(axis=1) / mask.sum(axis=1).clip(min=1e-9)
    norms = np.linalg.norm(pooled, axis=1, keepdims=True).clip(min=1e-9)
    return (pooled / norms).astype(np.float32)


def encode_text(text: str) -> np.ndarray:
    return _run_inference([text])[0]


def encode_texts(texts: list[str], batch_size: int = 64) -> list[np.ndarray]:
    if not texts:
        return []
    results = []
    for i in range(0, len(texts), batch_size):
        results.append(_run_inference(texts[i : i + batch_size]))
    return list(np.concatenate(results, axis=0))


# ---------------------------------------------------------------------------
# DB serialization helpers (unchanged)
# ---------------------------------------------------------------------------

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


def search_embeddings(query: str, rows, top_k: int = 5):
    if not rows:
        return []
    query_vector = _run_inference([query])  # (1, 384) already normalized

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

    embed_matrix = embed_matrix / np.linalg.norm(embed_matrix, axis=1, keepdims=True).clip(min=1e-9)
    query_norm = query_vector / np.linalg.norm(query_vector).clip(min=1e-9)

    scores = np.dot(embed_matrix, query_norm.T).flatten()
    top_indices = np.argsort(scores)[::-1][:top_k]

    return [(float(scores[i]), rows_only[i]) for i in top_indices]
