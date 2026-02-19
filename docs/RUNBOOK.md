# Runbook (Simple Demo)

## 1) Prerequisites
- Python 3.9+
- Atlas account (recommended) or local Docker

## 2) Configure Connection
```bash
cp .env.example .env
```
Edit `.env`:
- `MONGO_URI`: set your Atlas connection string
- `MONGO_DB`: default is `clinical_synth_demo`

## 3) Install Dependencies
```bash
make install
```

## 4) Create Dataset
```bash
make seed
```
Expected: prints `Seed complete` and shows counts for `participants/visits/clinical_notes`.

## 5) Create Indexes
```bash
make indexes
```
Expected: shows index creation for 3 collections.

## 6) Run Demo Queries
```bash
make demo
```
Expected: prints 5 query result blocks (structured/aggregation/text/hybrid).
This now also includes Q6, which lists visits containing CT attachment links.

## 7) Smoke Check
```bash
make smoke
```
Expected: `SMOKE PASS`.

## Common Issues
1. DNS / cluster host error
- Copy the full URI from Atlas `Connect -> Drivers` directly. Do not type it manually.

2. Authentication failed
- Check username/password.
- URL-encode special characters in password.

3. ServerSelectionTimeout
- Check Atlas Network Access and ensure your current IP is allowed.

4. Reset Dataset
```bash
make reset
```
