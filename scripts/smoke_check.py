from __future__ import annotations

import sys

from common import get_db, get_settings


REQUIRED_COLLECTIONS = ["participants", "visits", "clinical_notes"]
REQUIRED_INDEXES = {
    "participants": {"uid_participant_id", "idx_site_arm_age"},
    "visits": {"uid_participant_visit", "idx_visit_site_date", "idx_visit_attachment_modality"},
    "clinical_notes": {"txt_note_text", "idx_note_participant_created"},
}


def fail(msg: str) -> None:
    print(f"SMOKE FAIL: {msg}")
    sys.exit(1)


def main() -> None:
    settings = get_settings()
    db, client = get_db(settings)

    for col in REQUIRED_COLLECTIONS:
        count = db[col].count_documents({})
        if count == 0:
            fail(f"collection {col} is empty")

    for col, idx_names in REQUIRED_INDEXES.items():
        existing = set(db[col].index_information().keys())
        missing = idx_names - existing
        if missing:
            fail(f"collection {col} missing indexes: {sorted(missing)}")

    text_hits = db.clinical_notes.count_documents({"$text": {"$search": "fatigue"}})
    if text_hits == 0:
        fail("text search returned zero results for keyword 'fatigue'")

    ct_visits = db.visits.count_documents({"attachments.modality": "CT"})
    if ct_visits == 0:
        fail("no visits include CT attachment metadata")

    print("SMOKE PASS")
    client.close()


if __name__ == "__main__":
    main()
