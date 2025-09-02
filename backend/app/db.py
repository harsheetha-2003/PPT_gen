
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# from app.config import DB_PATH

# # SQLite engine
# engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})

# # Session factory
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Base class for models
# Base = declarative_base()

# # Dependency for FastAPI routes
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# import sqlite3
# import os
# import time
# from contextlib import contextmanager

# DB_PATH = "app_data.db"
# EXPIRY_SECONDS = 1800  # 30 min (change to 600 for 10 min)

# @contextmanager
# def get_connection():
#     conn = sqlite3.connect(DB_PATH)
#     try:
#         yield conn
#     finally:
#         conn.commit()
#         conn.close()

# # def init_db():
# #     """Initialize DB with files table."""
# #     with get_connection() as conn:
# #         conn.execute("""
# #             CREATE TABLE IF NOT EXISTS generated_files (
# #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
# #                 file_path TEXT NOT NULL,
# #                 file_type TEXT NOT NULL,   -- ppt or image
# #                 created_at INTEGER NOT NULL
# #             )
# #         """)

# def add_file(file_path: str, file_type: str):
#     """Insert file record into DB with timestamp."""
#     with get_connection() as conn:
#         conn.execute(
#             "INSERT INTO generated_files (file_path, file_type, created_at) VALUES (?, ?, ?)",
#             (file_path, file_type, int(time.time()))
#         )

# def get_valid_file(file_id: int):
#     """Return file path if within expiry window, else None."""
#     with get_connection() as conn:
#         cur = conn.execute("SELECT file_path, created_at FROM generated_files WHERE id=?", (file_id,))
#         row = cur.fetchone()
#         if row:
#             file_path, created_at = row
#             if time.time() - created_at <= EXPIRY_SECONDS:
#                 return file_path
#     return None

# def cleanup_expired():
#     """Remove expired files from disk + DB."""
#     with get_connection() as conn:
#         cur = conn.execute("SELECT id, file_path, created_at FROM generated_files")
#         for file_id, file_path, created_at in cur.fetchall():
#             if time.time() - created_at > EXPIRY_SECONDS:
#                 # delete from disk
#                 if os.path.exists(file_path):
#                     os.remove(file_path)
#                 # delete from db
#                 conn.execute("DELETE FROM generated_files WHERE id=?", (file_id,))


# def init_db():
#     """Initialize DB with required tables."""
#     conn = sqlite3.connect(DB_PATH)
#     cur = conn.cursor()

#     # Table for storing exports
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS export_records (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             filename TEXT NOT NULL,
#             filetype TEXT NOT NULL,
#             created_at TEXT NOT NULL
#         )
#     """)

#     # Table for caching searches
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS search_cache (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             query TEXT NOT NULL,
#             results TEXT NOT NULL,
#             created_at TEXT NOT NULL
#         )
#     """)

#     conn.commit()
#     conn.close()

# def save_generated_file(
#     kind: str,          # e.g., 'image', 'ppt', 'pdf'
#     file_id: str,       # UUID or unique identifier
#     path: str,          # absolute file path
#     ttl_minutes: int = 30
# ) -> int:
#     """
#     Save a generated file record to the database.
#     Returns the DB record ID.
#     """
#     with get_db_connection() as conn:
#         cur = conn.cursor()
#         cur.execute(
#             """
#             INSERT INTO generated_files (kind, file_id, path, created_at, expires_at)
#             VALUES (?, ?, ?, datetime('now'), datetime('now', ? || ' minutes'))
#             """,
#             (kind, file_id, path, ttl_minutes)
#         )
#         conn.commit()
#         return cur.lastrowid


# def save_export_record(filename: str, filetype: str):
#     """Save export metadata (PPT/PDF) to DB."""
#     conn = sqlite3.connect(DB_PATH)
#     cur = conn.cursor()
#     cur.execute(
#         "INSERT INTO export_records (filename, filetype, created_at) VALUES (?, ?, ?)",
#         (filename, filetype, datetime.utcnow().isoformat())
#     )
#     conn.commit()
#     conn.close()


# def get_export_records(limit: int = 20):
#     """Retrieve recent export records."""
#     conn = sqlite3.connect(DB_PATH)
#     cur = conn.cursor()
#     cur.execute(
#         "SELECT id, filename, filetype, created_at FROM export_records ORDER BY created_at DESC LIMIT ?",
#         (limit,)
#     )
#     rows = cur.fetchall()
#     conn.close()
#     return [
#         {"id": r[0], "filename": r[1], "filetype": r[2], "created_at": r[3]}
#         for r in rows
#     ]


# def save_search_cache(query: str, results: str):
#     """Save search query + results in DB."""
#     conn = sqlite3.connect(DB_PATH)
#     cur = conn.cursor()
#     cur.execute(
#         "INSERT INTO search_cache (query, results, created_at) VALUES (?, ?, ?)",
#         (query, results, datetime.utcnow().isoformat())
#     )
#     conn.commit()
#     conn.close()


# def get_search_cache(query: str):
#     """Retrieve cached results for a query (if any)."""
#     conn = sqlite3.connect(DB_PATH)
#     cur = conn.cursor()
#     cur.execute(
#         "SELECT results FROM search_cache WHERE query = ? ORDER BY created_at DESC LIMIT 1",
#         (query,)
#     )
#     row = cur.fetchone()
#     conn.close()
#     return row[0] if row else None

# def get_db_connection():
#     conn = sqlite3.connect(DB_PATH)
#     conn.row_factory = sqlite3.Row
#     return conn

# def fetch_export_by_id(export_id: int):
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM exports WHERE id = ?", (export_id,))
#     row = cur.fetchone()
#     conn.close()
#     return dict(row) if row else None

# def fetch_all_exports():
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM exports")
#     rows = cur.fetchall()
#     conn.close()
#     return [dict(row) for row in rows]

# def delete_expired_files() -> int:
#     """
#     Deletes files that have expired based on their TTL.
#     Removes the file from disk and the record from the database.
#     Returns the number of records deleted.
#     """
#     deleted_count = 0
#     with get_db_connection() as conn:
#         cur = conn.cursor()

#         # Check generated_files table
#         cur.execute("SELECT id, path FROM generated_files WHERE expires_at <= datetime('now')")
#         rows = cur.fetchall()
#         for row in rows:
#             record_id, path = row
#             try:
#                 if path and os.path.exists(path):
#                     os.remove(path)
#             except Exception:
#                 pass
#             cur.execute("DELETE FROM generated_files WHERE id = ?", (record_id,))
#             deleted_count += 1

#         # Check export_records table (if you also want to clean expired exports)
#         cur.execute("SELECT id, file_path FROM export_records WHERE expires_at <= datetime('now')")
#         rows = cur.fetchall()
#         for row in rows:
#             record_id, path = row
#             try:
#                 if path and os.path.exists(path):
#                     os.remove(path)
#             except Exception:
#                 pass
#             cur.execute("DELETE FROM export_records WHERE id = ?", (record_id,))
#             deleted_count += 1

#         conn.commit()
#     return deleted_count


import sqlite3
from typing import Optional, Dict, List

DB_PATH = "app.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def save_export_record(topic: str, audience: str, output_format: str, file_path: str) -> int:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO export_records (topic, audience, output_format, file_path)
            VALUES (?, ?, ?, ?)
            """,
            (topic, audience, output_format, file_path),
        )
        conn.commit()
        return cur.lastrowid

def save_generated_file(file_type: str, file_path: str) -> int:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO generated_files (file_type, file_path, created_at)
            VALUES (?, ?, ?)
        """, (file_type, file_path, datetime.utcnow().isoformat()))
        conn.commit()
        return cur.lastrowid

def fetch_export_by_id(record_id: int) -> Optional[Dict]:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM export_records WHERE id = ?", (record_id,))
        row = cur.fetchone()
        return dict(row) if row else None

def fetch_all_exports() -> List[Dict]:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM export_records ORDER BY id DESC")
        rows = cur.fetchall()
        return [dict(r) for r in rows]

def init_db():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS export_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                audience TEXT NOT NULL,
                output_format TEXT NOT NULL,
                file_path TEXT NOT NULL
            )
            """
        )
        conn.commit()
def delete_expired_files():
    expire_time = datetime.utcnow() - timedelta(days=EXPIRE_DAYS)
    with get_db_connection() as conn:
        cur = conn.cursor()
        # Fetch expired records
        cur.execute("SELECT id, file_path FROM generated_files WHERE created_at < ?", (expire_time.isoformat(),))
        rows = cur.fetchall()
        for row in rows:
            file_path = row["file_path"]
            try:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass
            # Delete DB record
            cur.execute("DELETE FROM generated_files WHERE id = ?", (row["id"],))
        conn.commit()

init_db()

