from src.lib.db import SessionLocal, backfill_fts_from_images
from src.models.Image import Image
from src.service.extractor import extract_text_from_image
from src.lib.llm import encode_texts
from src.lib.Timer import timer
import json
import os
from datetime import datetime, timezone
from concurrent.futures import ProcessPoolExecutor, as_completed

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
MAX_WORKERS = 14
EMBED_BATCH_SIZE = 64


def _process_one_ocr(args):
    """Worker: (full_path, directory_path) -> (rel_path, text) or None. OCR only, no embedding."""
    os.environ["OMP_THREAD_LIMIT"] = "1"
    full_path, directory_path = args
    try:
        rel_path = os.path.relpath(full_path, directory_path)
        text = extract_text_from_image(full_path)
        return (rel_path, text or "")
    except Exception:
        return None


def _progress_bar(done, total, width=30):
    if total <= 0:
        return "[" + " " * width + "] 0/0"
    filled = min(int(width * done / total), width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {done}/{total}"


@timer
def save_images(directory_path: str): 
    try:
        # 1. collect all the images
        paths = []
        for root, _dirs, files in os.walk(directory_path):
            for name in files:
                if os.path.splitext(name)[1].lower() not in IMAGE_EXTENSIONS:
                    continue
                full_path = os.path.join(root, name)
                paths.append((full_path, directory_path))


        # check preprocessed 
        rel_paths = [os.path.relpath(fp, dp) for fp, dp in paths]
        with SessionLocal() as db:
            existing = {row[0] for row in db.query(Image.image_loc).filter(Image.image_loc.in_(rel_paths)).all()}
            to_process = [(fp, dp) for fp, dp in paths if os.path.relpath(fp, dp) not in existing]
        if not to_process:
            print("No new images to save")
            return True

        total = len(to_process)

        # 1: OCR TODO : use the fast tessarat 
        results_by_index = [None] * total
        done = 0
        with ProcessPoolExecutor(max_workers=min(MAX_WORKERS, total)) as executor:
            future_to_idx = {executor.submit(_process_one_ocr, item): i for i, item in enumerate(to_process)}
            for fut in as_completed(future_to_idx):
                idx = future_to_idx[fut]
                r = fut.result()
                if r is not None:
                    results_by_index[idx] = r
                done += 1
                print(f"\r  OCR {_progress_bar(done, total)}", end="", flush=True)

        ocr_results = [r for r in results_by_index if r is not None]
        if not ocr_results:
            print("\nNo images succeeded OCR")
            return True

        print()
        # 4: Batch embed 
        texts = [t for _, t in ocr_results]
        embeddings = encode_texts(texts, batch_size=EMBED_BATCH_SIZE)

        now = datetime.now(timezone.utc)
        rows_for_db = [
            {"image_loc": rel_path, "words": text, "embeddings": json.dumps(emb.tolist()), "created_at": now}
            for (rel_path, text), emb in zip(ocr_results, embeddings)
        ]

        # Phase 3: Bulk insert + FTS backfill
        with SessionLocal() as db:
            last_id = db.query(Image.id).order_by(Image.id.desc()).limit(1).scalar() or 0
            db.bulk_insert_mappings(Image, rows_for_db)
            db.commit()
        backfill_fts_from_images(since_id=last_id)

        print(f"Saved {len(rows_for_db)} images")
    except Exception as e:
        print(f"\nError saving images: {e}")
        return False
    return True
