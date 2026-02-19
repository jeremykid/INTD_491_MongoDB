from __future__ import annotations

import argparse
import hashlib
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

from common import PROJECT_ROOT, get_db, get_settings

SITES = [f"SITE-{i:02d}" for i in range(1, 6)]
ARMS = ["drug_a", "drug_b", "placebo"]
SEXES = ["F", "M"]
STATUSES = ["active", "completed", "withdrawn"]
STATUS_WEIGHTS = [0.55, 0.35, 0.10]
SYMPTOMS = [
    "fatigue",
    "nausea",
    "headache",
    "dizziness",
    "insomnia",
    "joint pain",
    "chest discomfort",
    "cough",
    "anxiety",
    "appetite loss",
]
NOTE_TYPES = ["progress", "followup", "safety"]
AUTHOR_ROLES = ["study_nurse", "physician", "coordinator"]
ATTACHMENT_MODALITIES = ["CT", "MRI", "XR"]
ATTACHMENT_MODALITY_WEIGHTS = [0.70, 0.20, 0.10]
ATTACHMENT_FILE_TYPES = {
    "CT": "image/png",
    "MRI": "image/png",
    "XR": "image/png",
}
ATTACHMENT_FILE_EXTENSIONS = {
    "CT": "png",
    "MRI": "png",
    "XR": "png",
}
NOTE_TEMPLATES = [
    "participant reports {symptom_1} with occasional {symptom_2}; no urgent concerns.",
    "since last visit, {symptom_1} improved but {symptom_2} remains intermittent.",
    "today's review notes mild {symptom_1}; supportive advice provided for {symptom_2}.",
    "participant denies severe events, mentions {symptom_1} after activity and brief {symptom_2}.",
    "clinical impression: stable condition with low-grade {symptom_1} and episodic {symptom_2}.",
]


def weighted_choice(rng: random.Random, values: list[str], weights: list[float]) -> str:
    total = sum(weights)
    target = rng.random() * total
    cumulative = 0.0
    for value, weight in zip(values, weights):
        cumulative += weight
        if target <= cumulative:
            return value
    return values[-1]


def bounded_int(value: float, low: int, high: int) -> int:
    return max(low, min(high, int(round(value))))


def build_attachments(
    *,
    participant_id: str,
    site_id: str,
    visit_id: str,
    visit_date: datetime,
    rng: random.Random,
    force_ct: bool = False,
) -> list[dict]:
    attachment_probability = 0.35
    if not force_ct and rng.random() >= attachment_probability:
        return []

    attachment_count = 1 if rng.random() < 0.80 else 2
    attachments: list[dict] = []
    for attachment_no in range(1, attachment_count + 1):
        if force_ct and attachment_no == 1:
            modality = "CT"
        else:
            modality = weighted_choice(rng, ATTACHMENT_MODALITIES, ATTACHMENT_MODALITY_WEIGHTS)

        extension = ATTACHMENT_FILE_EXTENSIONS[modality]
        file_type = ATTACHMENT_FILE_TYPES[modality]
        lower_site = site_id.lower()
        lower_participant = participant_id.lower()
        lower_visit = visit_id.lower()
        storage_uri = (
            f"placeholder://imaging/{lower_site}/{lower_participant}/"
            f"{lower_visit}/{modality.lower()}_{attachment_no:02d}.{extension}"
        )

        attachments.append(
            {
                "attachment_id": f"ATT-{visit_id}-{attachment_no:02d}",
                "modality": modality,
                "file_type": file_type,
                "storage_uri": storage_uri,
                "description": f"Synthetic {modality} image placeholder",
                "captured_at": visit_date + timedelta(hours=2 + attachment_no),
                "synthetic_flag": True,
            }
        )
    return attachments


def build_manifest(db_name: str, participants: list[dict], visits: list[dict], notes: list[dict]) -> dict:
    visits_with_attachments = sum(1 for visit in visits if visit.get("attachments"))
    total_attachments = sum(len(visit.get("attachments", [])) for visit in visits)
    ct_attachments = sum(
        1
        for visit in visits
        for attachment in visit.get("attachments", [])
        if attachment.get("modality") == "CT"
    )
    serializable = {
        "db": db_name,
        "collections": {
            "participants": participants,
            "visits": visits,
            "clinical_notes": notes,
        },
    }
    payload = json.dumps(serializable, default=str, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return {
        "db": db_name,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "participants": len(participants),
            "visits": len(visits),
            "clinical_notes": len(notes),
            "visits_with_attachments": visits_with_attachments,
            "attachments": total_attachments,
            "ct_attachments": ct_attachments,
        },
        "sha256": digest,
    }


def parse_args(defaults: dict) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed synthetic clinical trial demo data into MongoDB.")
    parser.add_argument("--seed", type=int, default=defaults["seed"])
    parser.add_argument("--participants", type=int, default=defaults["participants"])
    parser.add_argument("--min-visits", type=int, default=defaults["min_visits"])
    parser.add_argument("--max-visits", type=int, default=defaults["max_visits"])
    parser.add_argument("--min-notes", type=int, default=defaults["min_notes"])
    parser.add_argument("--max-notes", type=int, default=defaults["max_notes"])
    parser.add_argument(
        "--drop-existing",
        action="store_true",
        default=defaults["drop_existing"],
        help="Drop existing collections before insert.",
    )
    return parser.parse_args()


def main() -> None:
    defaults = get_settings()
    args = parse_args(defaults)

    if args.min_visits > args.max_visits:
        raise ValueError("min-visits must be <= max-visits")
    if args.min_notes > args.max_notes:
        raise ValueError("min-notes must be <= max-notes")
    if args.participants <= 0:
        raise ValueError("participants must be > 0")

    rng = random.Random(args.seed)
    db_settings = defaults.copy()
    db, client = get_db(db_settings)

    if args.drop_existing:
        db.participants.drop()
        db.visits.drop()
        db.clinical_notes.drop()

    participants: list[dict] = []
    visits: list[dict] = []
    notes: list[dict] = []

    reference_date = datetime(2026, 1, 1, tzinfo=timezone.utc)

    for i in range(1, args.participants + 1):
        participant_id = f"SYN-P-{i:04d}"
        enrollment_date = reference_date - timedelta(days=rng.randint(160, 360))

        participant = {
            "participant_id": participant_id,
            "trial_id": "TRIAL-SYN-2026-001",
            "site_id": rng.choice(SITES),
            "arm": rng.choice(ARMS),
            "age": bounded_int(rng.gauss(52, 12), 18, 85),
            "sex_at_birth": rng.choice(SEXES),
            "enrollment_date": enrollment_date,
            "status": weighted_choice(rng, STATUSES, STATUS_WEIGHTS),
            "synthetic_flag": True,
        }
        participants.append(participant)

        visit_count = rng.randint(args.min_visits, args.max_visits)
        for visit_no in range(1, visit_count + 1):
            visit_id = f"{participant_id}-V{visit_no:02d}"
            visit_date = enrollment_date + timedelta(days=visit_no * 28 + rng.randint(-4, 4))
            force_ct = visit_no == 1 and i % 9 == 0
            attachments = build_attachments(
                participant_id=participant_id,
                site_id=participant["site_id"],
                visit_id=visit_id,
                visit_date=visit_date,
                rng=rng,
                force_ct=force_ct,
            )

            visit = {
                "visit_id": visit_id,
                "participant_id": participant_id,
                "site_id": participant["site_id"],
                "visit_no": visit_no,
                "visit_date": visit_date,
                "vitals": {
                    "systolic_bp": bounded_int(rng.gauss(122, 14), 90, 180),
                    "diastolic_bp": bounded_int(rng.gauss(78, 9), 55, 110),
                    "heart_rate": bounded_int(rng.gauss(74, 8), 45, 120),
                },
                "symptom_score": bounded_int(rng.gauss(4.2, 1.8), 0, 10),
                "protocol_deviation": rng.random() < 0.1,
                "synthetic_flag": True,
            }
            if attachments:
                visit["attachments"] = attachments
            visits.append(visit)

            note_count = rng.randint(args.min_notes, args.max_notes)
            for note_no in range(1, note_count + 1):
                symptom_1, symptom_2 = rng.sample(SYMPTOMS, 2)
                template = rng.choice(NOTE_TEMPLATES)
                text = template.format(symptom_1=symptom_1, symptom_2=symptom_2)
                note = {
                    "note_id": f"NOTE-{visit_id}-{note_no:02d}",
                    "participant_id": participant_id,
                    "visit_id": visit_id,
                    "site_id": participant["site_id"],
                    "note_type": rng.choice(NOTE_TYPES),
                    "author_role": rng.choice(AUTHOR_ROLES),
                    "note_text": f"Synthetic note: {text}",
                    "tags": sorted([symptom_1, symptom_2]),
                    "created_at": visit_date + timedelta(hours=note_no),
                    "synthetic_flag": True,
                }
                notes.append(note)

    participants.sort(key=lambda d: d["participant_id"])
    visits.sort(key=lambda d: (d["participant_id"], d["visit_no"]))
    notes.sort(key=lambda d: d["note_id"])

    db.participants.insert_many(participants, ordered=True)
    db.visits.insert_many(visits, ordered=True)
    db.clinical_notes.insert_many(notes, ordered=True)

    manifest = build_manifest(db.name, participants, visits, notes)
    out_path = PROJECT_ROOT / "data" / "generated" / "manifest.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("Seed complete")
    print(json.dumps(manifest, indent=2))

    client.close()


if __name__ == "__main__":
    main()
