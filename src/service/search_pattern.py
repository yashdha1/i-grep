from sqlalchemy import text
from src.lib.db import SessionLocal

def search_images_keyword(query: str, limit: int = 20):
    with SessionLocal() as session:
        rows = session.execute(
            text("""
                SELECT i.id, i.image_loc, i.words,
                       snippet(images_fts, 0, '**', '**', '...', 24) AS snippet
                FROM images_fts
                JOIN images i ON i.id = images_fts.rowid
                WHERE images_fts MATCH :q
                ORDER BY bm25(images_fts) LIMIT :lim
            """),
            {"q": query, "lim": limit},
        ).fetchall()
    return rows