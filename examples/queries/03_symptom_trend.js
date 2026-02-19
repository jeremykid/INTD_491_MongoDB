// Q3: aggregation trend

db.visits.aggregate([
  {
    $lookup: {
      from: "participants",
      localField: "participant_id",
      foreignField: "participant_id",
      as: "p"
    }
  },
  { $unwind: "$p" },
  {
    $group: {
      _id: { arm: "$p.arm", visit_no: "$visit_no" },
      avg_symptom_score: { $avg: "$symptom_score" },
      n: { $sum: 1 }
    }
  },
  {
    $project: {
      _id: 0,
      arm: "$_id.arm",
      visit_no: "$_id.visit_no",
      avg_symptom_score: { $round: ["$avg_symptom_score", 2] },
      n: 1
    }
  },
  { $sort: { arm: 1, visit_no: 1 } }
]);
