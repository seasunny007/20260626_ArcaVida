import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from config.settings import Settings, get_settings
from models.schemas import (
    AuditEvent,
    DeliveryRecord,
    DeliveryRecordCreate,
    DistributionPoint,
    DistributionPointCreate,
    MaterialNeed,
    MaterialNeedCreate,
    MaterialType,
    RecordStatus,
    RescueRecord,
    RescueRecordCreate,
    row_to_audit_event,
    row_to_delivery_record,
    row_to_distribution_point,
    row_to_material_need,
    row_to_record,
)


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
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS distribution_points (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            lat REAL,
            lng REAL,
            contact_person TEXT,
            contact_channel TEXT,
            population_served INTEGER,
            status TEXT NOT NULL DEFAULT 'ACTIVE',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS material_needs (
            id TEXT PRIMARY KEY,
            point_id TEXT NOT NULL,
            material_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            current_stock INTEGER NOT NULL DEFAULT 0,
            unit TEXT NOT NULL DEFAULT 'units',
            urgency TEXT NOT NULL DEFAULT 'MEDIUM',
            reported_by TEXT,
            reported_channel TEXT,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(point_id) REFERENCES distribution_points(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS delivery_records (
            id TEXT PRIMARY KEY,
            point_id TEXT NOT NULL,
            material_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit TEXT NOT NULL DEFAULT 'units',
            delivered_at TEXT NOT NULL,
            delivered_by TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(point_id) REFERENCES distribution_points(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_events (
            id TEXT PRIMARY KEY,
            action TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            details TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL
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


def record_audit_event(
    action: str,
    entity_type: str,
    entity_id: str,
    details: dict[str, object] | None = None,
    connection: sqlite3.Connection | None = None,
) -> str:
    owns_connection = connection is None
    conn = connection or connect()
    init_db(conn)
    event_id = str(uuid.uuid4())
    conn.execute(
        """
        INSERT INTO audit_events (id, action, entity_type, entity_id, details, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            action,
            entity_type,
            entity_id,
            json.dumps(details or {}, ensure_ascii=False),
            utc_now(),
        ),
    )
    conn.commit()
    if owns_connection:
        conn.close()
    return event_id


def create_distribution_point(
    data: DistributionPointCreate,
    connection: sqlite3.Connection | None = None,
) -> str:
    owns_connection = connection is None
    conn = connection or connect()
    init_db(conn)
    point_id = str(uuid.uuid4())
    now = utc_now()
    conn.execute(
        """
        INSERT INTO distribution_points (
            id, name, lat, lng, contact_person, contact_channel,
            population_served, status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            point_id,
            data.name,
            data.lat,
            data.lng,
            data.contact_person,
            data.contact_channel,
            data.population_served,
            data.status.value,
            now,
            now,
        ),
    )
    record_audit_event("create", "distribution_point", point_id, {"name": data.name}, conn)
    conn.commit()
    if owns_connection:
        conn.close()
    return point_id


def list_distribution_points(
    connection: sqlite3.Connection | None = None,
) -> list[DistributionPoint]:
    owns_connection = connection is None
    conn = connection or connect()
    rows = conn.execute("SELECT * FROM distribution_points ORDER BY name ASC").fetchall()
    if owns_connection:
        conn.close()
    return [row_to_distribution_point(dict(row)) for row in rows]


def get_distribution_point(
    point_id: str,
    connection: sqlite3.Connection | None = None,
) -> DistributionPoint | None:
    owns_connection = connection is None
    conn = connection or connect()
    row = conn.execute("SELECT * FROM distribution_points WHERE id = ?", (point_id,)).fetchone()
    if owns_connection:
        conn.close()
    return row_to_distribution_point(dict(row)) if row else None


def create_material_need(
    data: MaterialNeedCreate,
    connection: sqlite3.Connection | None = None,
) -> str:
    owns_connection = connection is None
    conn = connection or connect()
    init_db(conn)
    if not get_distribution_point(data.point_id, conn):
        if owns_connection:
            conn.close()
        raise ValueError("Distribution point not found")
    need_id = str(uuid.uuid4())
    now = utc_now()
    conn.execute(
        """
        INSERT INTO material_needs (
            id, point_id, material_type, quantity, current_stock, unit,
            urgency, reported_by, reported_channel, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            need_id,
            data.point_id,
            data.material_type.value,
            data.quantity,
            data.current_stock,
            data.unit,
            data.urgency.value,
            data.reported_by,
            data.reported_channel,
            now,
        ),
    )
    record_audit_event(
        "create",
        "material_need",
        need_id,
        {"point_id": data.point_id, "material_type": data.material_type.value},
        conn,
    )
    conn.commit()
    if owns_connection:
        conn.close()
    return need_id


def list_material_needs(
    point_id: str | None = None,
    material_type: MaterialType | None = None,
    connection: sqlite3.Connection | None = None,
) -> list[MaterialNeed]:
    owns_connection = connection is None
    conn = connection or connect()
    query = "SELECT * FROM material_needs"
    filters: list[str] = []
    params: list[str] = []
    if point_id:
        filters.append("point_id = ?")
        params.append(point_id)
    if material_type:
        filters.append("material_type = ?")
        params.append(material_type.value)
    if filters:
        query += " WHERE " + " AND ".join(filters)
    query += " ORDER BY updated_at DESC"
    rows = conn.execute(query, params).fetchall()
    if owns_connection:
        conn.close()
    return [row_to_material_need(dict(row)) for row in rows]


def create_delivery_record(
    data: DeliveryRecordCreate,
    connection: sqlite3.Connection | None = None,
) -> str:
    owns_connection = connection is None
    conn = connection or connect()
    init_db(conn)
    if not get_distribution_point(data.point_id, conn):
        if owns_connection:
            conn.close()
        raise ValueError("Distribution point not found")
    delivery_id = str(uuid.uuid4())
    now = utc_now()
    conn.execute(
        """
        INSERT INTO delivery_records (
            id, point_id, material_type, quantity, unit, delivered_at,
            delivered_by, notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            delivery_id,
            data.point_id,
            data.material_type.value,
            data.quantity,
            data.unit,
            now,
            data.delivered_by,
            data.notes,
            now,
        ),
    )
    conn.execute(
        """
        UPDATE material_needs
        SET current_stock = current_stock + ?, updated_at = ?
        WHERE point_id = ? AND material_type = ?
        """,
        (data.quantity, now, data.point_id, data.material_type.value),
    )
    record_audit_event(
        "create",
        "delivery_record",
        delivery_id,
        {"point_id": data.point_id, "material_type": data.material_type.value},
        conn,
    )
    conn.commit()
    if owns_connection:
        conn.close()
    return delivery_id


def list_delivery_records(
    point_id: str | None = None,
    connection: sqlite3.Connection | None = None,
) -> list[DeliveryRecord]:
    owns_connection = connection is None
    conn = connection or connect()
    if point_id:
        rows = conn.execute(
            "SELECT * FROM delivery_records WHERE point_id = ? ORDER BY delivered_at DESC",
            (point_id,),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM delivery_records ORDER BY delivered_at DESC").fetchall()
    if owns_connection:
        conn.close()
    return [row_to_delivery_record(dict(row)) for row in rows]


def list_audit_events(connection: sqlite3.Connection | None = None) -> list[AuditEvent]:
    owns_connection = connection is None
    conn = connection or connect()
    rows = conn.execute("SELECT * FROM audit_events ORDER BY created_at DESC").fetchall()
    if owns_connection:
        conn.close()
    return [row_to_audit_event(dict(row)) for row in rows]
