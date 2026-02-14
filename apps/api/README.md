# API (MVP)

## Prerequisites

Install poppler (`pdftoppm`):

- macOS: `brew install poppler`
- Ubuntu/Debian: `sudo apt-get update && sudo apt-get install -y poppler-utils`

## Run

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn apps.api.main:app --reload --port 8000
```

## Endpoints

- `POST /v1/upload` (multipart form field `file`) → `{ document_id }`
- `GET /v1/docs/{doc_id}/page/{page}?user_id=anon&paid=false` → mobile-friendly HTML
- `GET /v1/docs/{doc_id}/pages/{page}.png` → rendered PNG (cached)

## Notes

Quota is file-based (`data/quota.json`) and keyed by UTC day + `user_id`.
