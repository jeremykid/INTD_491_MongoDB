// Q4: text search

db.clinical_notes.find(
  { $text: { $search: "fatigue nausea" } },
  { _id: 0, participant_id: 1, visit_id: 1, note_text: 1, score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } }).limit(10);
