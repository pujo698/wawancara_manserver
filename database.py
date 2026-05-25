import sqlite3
import json
import logging
import os

logger = logging.getLogger(__name__)

DB_PATH = "interviews.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                session_id TEXT PRIMARY KEY,
                history TEXT
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("Database SQLite berhasil diinisialisasi.")
    except Exception as e:
        logger.error(f"Gagal inisialisasi database: {e}")

def get_history(session_id: str) -> list:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT history FROM chat_history WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return json.loads(row[0])
        return []
    except Exception as e:
        logger.error(f"Gagal mengambil riwayat chat: {e}")
        return []

def save_history(session_id: str, history: list):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        history_json = json.dumps(history)
        cursor.execute('''
            INSERT INTO chat_history (session_id, history)
            VALUES (?, ?)
            ON CONFLICT(session_id) DO UPDATE SET history = excluded.history
        ''', (session_id, history_json))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Gagal menyimpan riwayat chat: {e}")

def clear_history(session_id: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()
        logger.info(f"Sesi wawancara direset untuk {session_id}")
    except Exception as e:
        logger.error(f"Gagal menghapus riwayat chat: {e}")
