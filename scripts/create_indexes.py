from __future__ import annotations

from pymongo import ASCENDING, DESCENDING, TEXT

from common import get_db, get_settings


def main() -> None:
    settings = get_settings()
    db, client = get_db(settings)

    created = {
        "participants": [
            db.participants.create_index(
                [("participant_id", ASCENDING)],
                unique=True,
                name="uid_participant_id",
            ),
            db.participants.create_index(
                [("site_id", ASCENDING), ("arm", ASCENDING), ("age", ASCENDING)],
                name="idx_site_arm_age",
            ),
        ],
        "visits": [
            db.visits.create_index(
                [("participant_id", ASCENDING), ("visit_no", ASCENDING)],
                unique=True,
                name="uid_participant_visit",
            ),
            db.visits.create_index(
                [("site_id", ASCENDING), ("visit_date", DESCENDING)],
                name="idx_visit_site_date",
            ),
            db.visits.create_index(
                [("attachments.modality", ASCENDING), ("visit_date", DESCENDING)],
                name="idx_visit_attachment_modality",
            ),
        ],
        "clinical_notes": [
            db.clinical_notes.create_index(
                [("note_text", TEXT)],
                default_language="english",
                name="txt_note_text",
            ),
            db.clinical_notes.create_index(
                [("participant_id", ASCENDING), ("created_at", DESCENDING)],
                name="idx_note_participant_created",
            ),
        ],
    }

    print("Indexes created:")
    for col, names in created.items():
        print(f"- {col}: {', '.join(names)}")

    client.close()


if __name__ == "__main__":
    main()
