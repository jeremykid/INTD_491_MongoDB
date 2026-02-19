// Q2: aggregation completion rate

db.participants.aggregate([
  {
    $group: {
      _id: "$arm",
      total: { $sum: 1 },
      completed: { $sum: { $cond: [{ $eq: ["$status", "completed"] }, 1, 0] } }
    }
  },
  {
    $project: {
      _id: 0,
      arm: "$_id",
      total: 1,
      completed: 1,
      completion_rate: { $round: [{ $divide: ["$completed", "$total"] }, 3] }
    }
  },
  { $sort: { arm: 1 } }
]);
