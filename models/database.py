import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from config.settings import Settings, get_settings
from models.schemas import RecordStatus, RescueRecord, RescueRecordCreate, row_to_record


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect(database_path: Path | None = None) -> sqlite3.Connection:
    settings = get_settings()
    path = database_path or settings.sqlite_path(settings.database_url)
    if str(path) != ":memory:":
        path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(path))
    connection.row_factory = sqlite3.Row
    return connection


def init_db(connection: sqlite3.Connection | None = None) -> None:
    owns_connection = connection is None
    conn = connection or connect()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS rescue_records (
            id TEXT PRIMARY KEY,
            raw_text TEXT NOT NULL,
            detected_lang TEXT NOT NULL,
            translated_text TEXT NOT NULL,
            location TEXT NOT NULL DEFAULT '',
            needs TEXT NOT NULL DEFAULT '[]',
            trapped INTEGER NOT NULL DEFAULT 0,
            priority INTEGER NOT NULL DEFAULT 1,
            slang_alert INTEGER NOT NULL DEFAULT 0,
            slang_hint TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            volunteer_notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            source_chat_id TEXT NOT NULL
        )
        """
    )
    conn.commit()
    if owns_connection:
        conn.close()


def hash_chat_id(source_chat_id: str, settings: Settings | None = None) -> str:
    active_settings = settings or get_settings()
    payload = f"{active_settings.source_chat_hash_salt}:{source_chat_id}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def create_record(data: RescueRecordCreate, connection: sqlite3.Connection | None = None) -> str:
    owns_connection = connection is None
    conn = connection or connect()
    init_db(conn)
    record_id = str(uuid.uuid4())
    now = utc_now()
    source_hash = hash_chat_id(data.source_chat_id)

    conn.execute(
        """
        INSERT INTO rescue_records (
            id, raw_text, detected_lang, translated_text, location, needs,
            trapped, priority, slang_alert, slang_hint, status,
            volunteer_notes, created_at, updated_at, source_chat_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record_id,
            data.raw_text,
            data.detected_lang,
            data.translated_text,
            data.location,
            json.dumps(data.needs, ensure_ascii=False),
            int(data.trapped),
            data.priority,
            int(data.slang_alert),
            data.slang_hint,
            RecordStatus.pending.value,
            "",
            now,
            now,
            source_hash,
        ),
    )
    conn.commit()
    if owns_connection:
        conn.close()
    return record_id


def get_record(record_id: str, connection: sqlite3.Connection | None = None) -> RescueRecord | None:
    owns_connection = connection is None
    conn = connection or connect()
    row = conn.execute("SELECT * FROM rescue_records WHERE id = ?", (record_id,)).fetchone()
    if owns_connection:
        conn.close()
    return row_to_record(dict(row)) if row else None


def list_records(
    status: RecordStatus | None = None,
    connection: sqlite3.Connection | None = None,
) -> list[RescueRecord]:
    owns_connection = connection is None
    conn = connection or connect()
    if status:
        rows = conn.execute(
            "SELECT * FROM rescue_records WHERE status = ? ORDER BY priority DESC, created_at ASC",
            (status.value,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM rescue_records ORDER BY priority DESC, created_at ASC"
        ).fetchall()
    if owns_connection:
        conn.close()
    return [row_to_record(dict(row)) for row in rows]


def update_status(
    record_id: str,
    status: RecordStatus,
    connection: sqlite3.Connection | None = None,
) -> bool:
    owns_connection = connection is None
    conn = connection or connect()
    cursor = conn.execute(
        "UPDATE rescue_records SET status = ?, updated_at = ? WHERE id = ?",
        (status.value, utc_now(), record_id),
    )
    conn.commit()
    if owns_connection:
        conn.close()
    return cursor.rowcount > 0


def add_note(record_id: str, note: str, connection: sqlite3.Connection | None = None) -> bool:
    owns_connection = connection is None
    conn = connection or connect()
    cursor = conn.execute(
        "UPDATE rescue_records SET volunteer_notes = ?, updated_at = ? WHERE id = ?",
        (note, utc_now(), record_id),
    )
    conn.commit()
    if owns_connection:
        conn.close()
    return cursor.rowcount > 0
