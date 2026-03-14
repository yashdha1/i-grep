from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

# Ensure data directory exists (SQLite won't create parent dirs)
_db_path = Path(__file__).resolve().parent.parent.parent / "data" / "database.db"
_db_path.parent.mkdir(parents=True, exist_ok=True)
_db_url = f"sqlite:///{_db_path.as_posix()}"

engine = create_engine(
    _db_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

FTS_TABLE = "images_fts"


def backfill_fts_from_images(since_id=None):
    """Insert into FTS table for image rows"""
    eng = engine
    with eng.connect() as conn:
        if since_id is None:
            conn.execute(text(
                "INSERT INTO images_fts(rowid, words) SELECT id, words FROM images "
                "WHERE id NOT IN (SELECT rowid FROM images_fts)"
            ))
        else:
            conn.execute(text(
                "INSERT INTO images_fts(rowid, words) SELECT id, words FROM images WHERE id > :since_id"
            ), {"since_id": since_id})
        conn.commit()


def create_fts_table(engine=None):
    """Create the FTS5 virtual table and backfill from images. For faster lookup of the keywords."""
    with engine.connect() as conn:
        conn.execute(text(
            "CREATE VIRTUAL TABLE IF NOT EXISTS images_fts USING fts5(words, content='images', content_rowid='id')"
        ))
        conn.execute(text(
            "INSERT INTO images_fts(rowid, words) SELECT id, words FROM images "
            "WHERE id NOT IN (SELECT rowid FROM images_fts)"
        ))
        conn.commit()
        print("FTS5 virtual table created successfully")

def init_db():
    """Initialize the database and create the FTS5 virtual table."""
    # Import models so they register with Base.metadata before create_all()
    from src.models.Image import Image  # noqa: F401
    Base.metadata.create_all(bind=engine)
    create_fts_table(engine)