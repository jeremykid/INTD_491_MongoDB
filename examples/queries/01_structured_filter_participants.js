// Q1: structured filter

db.participants.find(
  { arm: "drug_a", site_id: "SITE-03", age: { $gte: 40, $lte: 65 } },
  { _id: 0, participant_id: 1, age: 1, arm: 1, site_id: 1 }
).sort({ age: 1 });
