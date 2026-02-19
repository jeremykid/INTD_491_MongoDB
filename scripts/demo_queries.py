from __future__ import annotations

from bson.json_util import dumps

from common import get_db, get_settings


def print_block(title: str, docs: list[dict]) -> None:
    print(f"\n=== {title} (count={len(docs)}) ===")
    preview = docs[:5]
    for doc in preview:
        print(dumps(doc, ensure_ascii=False))
    if len(docs) > 5:
        print("...")


def main() -> None:
    settings = get_settings()
    db, client = get_db(settings)

    q1 = list(
        db.participants.find(
            {"arm": "drug_a", "site_id": "SITE-03", "age": {"$gte": 40, "$lte": 65}},
            {"_id": 0, "participant_id": 1, "age": 1, "arm": 1, "site_id": 1},
        ).sort("age", 1)
    )
    print_block("Q1 structured filter participants", q1)

    q2 = list(
        db.participants.aggregate(
            [
                {
                    "$group": {
                        "_id": "$arm",
                        "total": {"$sum": 1},
                        "completed": {
                            "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
                        },
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "arm": "$_id",
                        "total": 1,
                        "completed": 1,
                        "completion_rate": {
                            "$round": [{"$divide": ["$completed", "$total"]}, 3]
                        },
                    }
                },
                {"$sort": {"arm": 1}},
            ]
        )
    )
    print_block("Q2 completion rate by arm", q2)

    q3 = list(
        db.visits.aggregate(
            [
                {
                    "$lookup": {
                        "from": "participants",
                        "localField": "participant_id",
                        "foreignField": "participant_id",
                        "as": "p",
                    }
                },
                {"$unwind": "$p"},
                {
                    "$group": {
                        "_id": {"arm": "$p.arm", "visit_no": "$visit_no"},
                        "avg_symptom_score": {"$avg": "$symptom_score"},
                        "n": {"$sum": 1},
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "arm": "$_id.arm",
                        "visit_no": "$_id.visit_no",
                        "avg_symptom_score": {"$round": ["$avg_symptom_score", 2]},
                        "n": 1,
                    }
                },
                {"$sort": {"arm": 1, "visit_no": 1}},
            ]
        )
    )
    print_block("Q3 symptom trend by arm", q3)

    q4 = list(
        db.clinical_notes.find(
            {"$text": {"$search": "fatigue nausea"}},
            {
                "_id": 0,
                "participant_id": 1,
                "visit_id": 1,
                "note_text": 1,
                "score": {"$meta": "textScore"},
            },
        )
        .sort([("score", {"$meta": "textScore"})])
        .limit(10)
    )
    print_block("Q4 text search notes", q4)

    q5 = list(
        db.clinical_notes.aggregate(
            [
                {"$match": {"$text": {"$search": "\"chest discomfort\" fatigue"}}},
                {
                    "$lookup": {
                        "from": "participants",
                        "localField": "participant_id",
                        "foreignField": "participant_id",
                        "as": "p",
                    }
                },
                {"$unwind": "$p"},
                {"$match": {"p.arm": "drug_a", "p.age": {"$gte": 50}}},
                {
                    "$group": {
                        "_id": "$p.site_id",
                        "note_hits": {"$sum": 1},
                        "participants": {"$addToSet": "$participant_id"},
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "site_id": "$_id",
                        "note_hits": 1,
                        "unique_participants": {"$size": "$participants"},
                    }
                },
                {"$sort": {"note_hits": -1}},
            ]
        )
    )
    print_block("Q5 hybrid text + structured filter", q5)

    q6 = list(
        db.visits.aggregate(
            [
                {
                    "$addFields": {
                        "ct_attachments": {
                            "$filter": {
                                "input": "$attachments",
                                "as": "attachment",
                                "cond": {"$eq": ["$$attachment.modality", "CT"]},
                            }
                        }
                    }
                },
                {"$match": {"ct_attachments.0": {"$exists": True}}},
                {
                    "$project": {
                        "_id": 0,
                        "visit_id": 1,
                        "participant_id": 1,
                        "site_id": 1,
                        "ct_count": {"$size": "$ct_attachments"},
                        "ct_uris": "$ct_attachments.storage_uri",
                    }
                },
                {"$sort": {"visit_id": 1}},
                {"$limit": 10},
            ]
        )
    )
    print_block("Q6 visits with CT attachment links", q6)

    client.close()


if __name__ == "__main__":
    main()
