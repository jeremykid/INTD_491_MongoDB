# INTD_491_MongoDB (Simple Demo)

This is a minimal MongoDB teaching demo using **fully synthetic clinical trial data** to show:
- structured query
- aggregation
- text search
- hybrid (text + structured) query
- optional imaging metadata links (for example CT placeholders) connected to visits

## Synthetic Disclaimer
This repository contains synthetic data only (`synthetic_flag: true`) for educational use.
It must not be used for real medical decision-making.

## Recommended Workflow (Atlas)
```bash
cd INTD_491_MongoDB
cp .env.example .env
# Edit .env and set your Atlas MONGO_URI

make install
make seed
make indexes
make demo
make smoke
```

## Optional: Local Docker MongoDB
If you want to run MongoDB locally:
```bash
make up
make seed
make indexes
make demo
make smoke
```

## Commands
- `make up`: Start local MongoDB + mongo-express (Docker)
- `make down`: Stop local containers
- `make install`: Install Python dependencies
- `make seed`: Generate and insert synthetic dataset
- `make indexes`: Create indexes
- `make demo`: Run demo queries
- `make smoke`: Run smoke checks
- `make reset`: Clear collections and reseed

## Demo Data Examples
- Document samples: `docs/DEMO_DATA_EXAMPLES.md`
- Data model: `docs/DATA_MODEL.md`
- Runbook: `docs/RUNBOOK.md`
- Synthetic data policy: `docs/SYNTHETIC_DATA_POLICY.md`

## Default Dataset Size
- participants: 100
- visits: 3-5 per participant
- clinical notes: 1-4 per visit
- a subset of visits include `attachments` metadata with CT/MRI/XR placeholder URIs

## Core Structure
```text
scripts/
  common.py
  seed_data.py
  create_indexes.py
  demo_queries.py
  smoke_check.py
examples/queries/
  01_structured_filter_participants.js
  02_completion_rate_by_arm.js
  03_symptom_trend.js
  04_text_search_notes.js
  05_hybrid_text_structured.js
  06_visits_with_ct_attachments.js
docs/
  RUNBOOK.md
  DEMO_DATA_EXAMPLES.md
  DATA_MODEL.md
  SYNTHETIC_DATA_POLICY.md
```
