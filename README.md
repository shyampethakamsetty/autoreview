# Cube Assessment — Starter Repo

This is a minimal starter scaffold for the Cube assessment.
It includes a FastAPI backend skeleton, a Vite + React frontend scaffold (TypeScript), Dockerfiles, docker-compose, seed data, and basic tests.

## Quick start (local)

### Backend (dev)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend (dev)
```bash
cd frontend
npm ci
npm run dev
```

### Docker (all services)
```bash
docker-compose up --build
```

## Notes
- Provide OPENAI_API_KEY in `.env` if you want to enable LLM features.
- `requests.http` contains example API calls.
