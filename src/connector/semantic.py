from src.lib.db import SessionLocal 
from src.models.Image import Image 
from src.service.console_output import print_search_results
from src.lib.llm import search_embeddings
import os
from src.lib.Timer import timer

@timer
def semantic_search(query: str, top_k: int = 5):
    with SessionLocal() as session:
                db_rows = session.query(Image).all()
    results = search_embeddings(query, db_rows, top_k=top_k)
    print_search_results(None, results, images_dir=os.getenv("IMAGE_DIR"))