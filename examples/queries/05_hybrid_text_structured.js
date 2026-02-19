// Q5: hybrid text + structured

db.clinical_notes.aggregate([
  { $match: { $text: { $search: "\"chest discomfort\" fatigue" } } },
  {
    $lookup: {
      from: "participants",
      localField: "participant_id",
      foreignField: "participant_id",
      as: "p"
    }
  },
  { $unwind: "$p" },
  { $match: { "p.arm": "drug_a", "p.age": { $gte: 50 } } },
  {
    $group: {
      _id: "$p.site_id",
      note_hits: { $sum: 1 },
      participants: { $addToSet: "$participant_id" }
    }
  },
  {
    $project: {
      _id: 0,
      site_id: "$_id",
      note_hits: 1,
      unique_participants: { $size: "$participants" }
    }
  },
  { $sort: { note_hits: -1 } }
]);
