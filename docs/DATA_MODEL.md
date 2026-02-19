# Data Model (Simple Demo)

## Collections
- `participants`: structured participant-level data
- `visits`: structured longitudinal visit data
- `clinical_notes`: unstructured narrative notes

## Key design choices
- `participants` keeps stable participant attributes only.
- `visits` is referenced by `participant_id` for growth and aggregation.
- `clinical_notes` is separated for text search and hybrid analytics.
- `vitals` is embedded in `visits` because it shares visit lifecycle.
- `attachments` metadata is embedded in `visits` as an optional array.
  Each attachment stores modality (`CT`/`MRI`/`XR`) and a synthetic placeholder URI.

## Why referenced instead of fully embedded?
- Easier to run cross-collection aggregations with `$lookup`.
- Better control for index strategy per data type.
- More realistic for medium-size clinical data demos.

## Attachment shape (embedded in visits)
```json
{
  "attachment_id": "ATT-SYN-P-0001-V03-01",
  "modality": "CT",
  "file_type": "image/png",
  "storage_uri": "placeholder://imaging/site-03/syn-p-0001/syn-p-0001-v03/ct_01.png",
  "description": "Synthetic CT image placeholder",
  "captured_at": "2025-05-20T03:00:00Z",
  "synthetic_flag": true
}
```
