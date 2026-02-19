// Q6: visits with CT attachment links

db.visits.aggregate([
  {
    $addFields: {
      ct_attachments: {
        $filter: {
          input: "$attachments",
          as: "attachment",
          cond: { $eq: ["$$attachment.modality", "CT"] }
        }
      }
    }
  },
  { $match: { "ct_attachments.0": { $exists: true } } },
  {
    $project: {
      _id: 0,
      visit_id: 1,
      participant_id: 1,
      site_id: 1,
      ct_count: { $size: "$ct_attachments" },
      ct_uris: "$ct_attachments.storage_uri"
    }
  },
  { $sort: { visit_id: 1 } },
  { $limit: 10 }
]);
