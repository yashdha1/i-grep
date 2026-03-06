from sqlalchemy import Column, Integer, String, Text, DateTime, event, text
from datetime import datetime, timezone
from src.lib.db import Base, FTS_TABLE


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    image_loc = Column(String, nullable=False)
    words = Column(Text, nullable=False)
    embeddings = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))


# FTS Connection helpers: 
def _sync_fts_insert(mapper, connection, target):
    connection.execute(
        text(f"INSERT INTO {FTS_TABLE}(rowid, words) VALUES (:id, :words)"),
        {"id": target.id, "words": target.words or ""},
    )


def _sync_fts_update(mapper, connection, target):
    connection.execute(text(f"DELETE FROM {FTS_TABLE} WHERE rowid = :id"), {"id": target.id})
    connection.execute(
        text(f"INSERT INTO {FTS_TABLE}(rowid, words) VALUES (:id, :words)"),
        {"id": target.id, "words": target.words or ""},
    )


def _sync_fts_delete(mapper, connection, target):
    connection.execute(text(f"DELETE FROM {FTS_TABLE} WHERE rowid = :id"), {"id": target.id})


event.listens_for(Image, "after_insert")(_sync_fts_insert)
event.listens_for(Image, "after_update")(_sync_fts_update)
event.listens_for(Image, "after_delete")(_sync_fts_delete)