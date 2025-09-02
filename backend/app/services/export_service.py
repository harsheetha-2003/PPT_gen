# import os
# import shutil
# import uuid
# from fastapi import APIRouter, HTTPException
# from fastapi.responses import FileResponse
# from apscheduler.schedulers.background import BackgroundScheduler
# from db import add_file, get_valid_file, cleanup_expired, init_db

# EXPORT_DIR_PPT = "generated_ppts"
# EXPORT_DIR_IMG = "generated_images"

# # Ensure directories exist
# os.makedirs(EXPORT_DIR_PPT, exist_ok=True)
# os.makedirs(EXPORT_DIR_IMG, exist_ok=True)

# # Init DB
# init_db()

# # Setup scheduler for cleanup
# scheduler = BackgroundScheduler()
# scheduler.add_job(cleanup_expired, "interval", minutes=5)
# scheduler.start()

# router = APIRouter()

# def save_ppt(ppt_path: str) -> int:
#     """Save PPT to generated_ppts with unique name, record in DB, return file_id."""
#     unique_name = f"{uuid.uuid4()}.pptx"
#     dest = os.path.join(EXPORT_DIR_PPT, unique_name)
#     shutil.move(ppt_path, dest)
#     add_file(dest, "ppt")
#     return unique_name

# def save_image(img_path: str) -> int:
#     """Save image to generated_images with unique name, record in DB, return file_id."""
#     unique_name = f"{uuid.uuid4()}.png"
#     dest = os.path.join(EXPORT_DIR_IMG, unique_name)
#     shutil.move(img_path, dest)
#     add_file(dest, "image")
#     return unique_name

# @router.get("/download/{file_id}")
# def download_file(file_id: int):
#     """Allow file download if within expiry time."""
#     file_path = get_valid_file(file_id)
#     if not file_path or not os.path.exists(file_path):
#         raise HTTPException(status_code=404, detail="File expired or not found")
#     return FileResponse(file_path, filename=os.path.basename(file_path))

# export_service.py
# backend/app/services/export_service.py
# import sqlite3
# from typing import Optional, Dict, List, Any
# from contextlib import contextmanager
# import os
# from datetime import datetime, timedelta
# from app import config

# # Database file path
# DB_FILE = getattr(config, "DB_FILE", "app_data.db")

# # Ensure the database file exists
# if not os.path.exists(DB_FILE):
#     # Create tables if DB does not exist
#     with sqlite3.connect(DB_FILE) as conn:
#         cur = conn.cursor()
#         cur.execute("""
#         CREATE TABLE IF NOT EXISTS export_records (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             topic TEXT NOT NULL,
#             audience TEXT NOT NULL,
#             output_format TEXT NOT NULL,
#             file_path TEXT NOT NULL,
#             created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
#         )
#         """)
#         conn.commit()


# @contextmanager
# def get_db_connection():
#     """
#     Context manager for SQLite connection.
#     """
#     conn = sqlite3.connect(DB_FILE)
#     conn.row_factory = sqlite3.Row  # allows dict-like access
#     try:
#         yield conn
#     finally:
#         conn.close()


# def save_export_record(topic: str, audience: str, output_format: str, file_path: str) -> int:
#     """
#     Save a new export record into the database.
#     Returns the record id.
#     """
#     with get_db_connection() as conn:
#         cur = conn.cursor()
#         cur.execute("""
#             INSERT INTO export_records (topic, audience, output_format, file_path, created_at)
#             VALUES (?, ?, ?, ?, ?)
#         """, (topic, audience, output_format, file_path, datetime.now()))
#         conn.commit()
#         return cur.lastrowid


# def fetch_export_by_id(record_id: int) -> Optional[Dict[str, Any]]:
#     """
#     Fetch a single export record by its ID.
#     """
#     with get_db_connection() as conn:
#         cur = conn.cursor()
#         cur.execute("SELECT * FROM export_records WHERE id = ?", (record_id,))
#         row = cur.fetchone()
#         if row:
#             return dict(row)
#         return None


# def fetch_all_exports() -> List[Dict[str, Any]]:
#     """
#     Fetch all export records ordered by newest first.
#     """
#     with get_db_connection() as conn:
#         cur = conn.cursor()
#         cur.execute("SELECT * FROM export_records ORDER BY created_at DESC")
#         rows = cur.fetchall()
#         return [dict(r) for r in rows]



# def cleanup_expired_exports(ttl_minutes: int = 30):
#     """
#     Optional helper: Delete exports older than TTL.
#     """
#     expire_time = datetime.now() - timedelta(minutes=ttl_minutes)
#     with get_db_connection() as conn:
#         cur = conn.cursor()
#         cur.execute("SELECT id, file_path FROM export_records WHERE created_at < ?", (expire_time,))
#         rows = cur.fetchall()
#         for r in rows:
#             file_path = r["file_path"]
#             try:
#                 if file_path and os.path.exists(file_path):
#                     os.remove(file_path)
#             except Exception:
#                 pass
#             cur.execute("DELETE FROM export_records WHERE id = ?", (r["id"],))
#         conn.commit()

import os
from typing import Optional, Dict, Any
from app.db import save_export_record, fetch_export_by_id, fetch_all_exports, get_db_connection

DOWNLOAD_URL_PREFIX = "/api/export/download"
ALLOWED_FORMATS = {"pptx", "pdf"}

def save_and_record_export(
    file_path: str,
    topic: Optional[str] = None,
    audience: Optional[str] = None,
    output_format: str = "pptx"
) -> Dict[str, Any]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    output_fmt = (output_format or "pptx").lower()
    if output_fmt not in ALLOWED_FORMATS:
        raise ValueError(f"Unsupported format: {output_fmt}")

    topic_val = topic or "Unknown"
    audience_val = audience or "General Public"

    record_id = save_export_record(topic_val, audience_val, output_fmt, file_path)
    download_url = f"{DOWNLOAD_URL_PREFIX}/{record_id}"

    return {"record_id": record_id, "download_url": download_url, "file_path": file_path}

def get_export_record(record_id: int) -> Optional[Dict[str, Any]]:
    return fetch_export_by_id(record_id)

def list_all_exports() -> list:
    return fetch_all_exports()

def delete_export_record(record_id: int) -> bool:
    rec = get_export_record(record_id)
    file_path = rec.get("file_path") if rec else None

    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass

    if rec:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM export_records WHERE id = ?", (record_id,))
            conn.commit()
        return True

    return False

# ---------------------------------------------------
# Helper to fetch file path by export record ID
# ---------------------------------------------------
def get_file_path(record_id: int) -> str:
    """
    Return the file path of an export record, or None if not found.
    """
    rec = get_export_record(record_id)
    return rec.get("file_path") if rec else None