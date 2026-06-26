import sqlite3

from models.database import create_record, get_record, init_db, update_status
from models.schemas import RecordStatus, RescueRecordCreate


def test_create_and_update_record_in_memory_db() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    init_db(connection)

    record_id = create_record(
        RescueRecordCreate(
            raw_text="necesita agua",
            detected_lang="es",
            translated_text="需要水",
            location="Caracas",
            needs=["水"],
            source_chat_id="12345",
        ),
        connection,
    )

    assert update_status(record_id, RecordStatus.verified, connection) is True
    record = get_record(record_id, connection)
    assert record is not None
    assert record.status == RecordStatus.verified
    assert record.source_chat_id != "12345"
