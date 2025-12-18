# Team Gotthard — Application

This folder contains the frontend (Vue 3 + Vite) and the backend (FastAPI) for the Team Gotthard Panorama Express prototype.

This README explains how to start both the frontend and the backend locally for development.

## Prerequisites

- Node.js (recommended v20.x or later) and npm
- Python 3.10+ (3.11 recommended)
- Git (optional)

Make sure `node` and `npm` are available in your PATH and that `python` points to a recent Python installation.

## Backend (FastAPI)

The backend lives in `./backend` and uses FastAPI + SQLModel with a local PostgreSQL database.

1. Create and activate a Python virtual environment (recommended):

```bash
cd Application/backend
python -m venv .venv
source .venv/bin/activate
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

Note: `requirements.txt` in this prototype contains a large set of packages. If you prefer a minimal setup, at minimum install:

```bash
pip install fastapi uvicorn sqlmodel sqlalchemy
```

3. Start the backend development server `Application`:

```bash
cd Application
uvicorn backend.main:app --reload
```

The API will be available at: http://127.0.0.1:8000

Open the interactive docs at: http://127.0.0.1:8000/docs

The backend will auto-create a local SQLite database at `Application/backend/database.db` on first run. (only for first prototyping)

## Frontend (Vue 3 + Vite)

The frontend lives in `./frontend` and is a Vite + Vue 3 application.
Frontend is automatically started with the backend and doesn't need to get started sepearte.

1. Install node dependencies:

```bash
cd Application/frontend
npm install
```

2. Start the dev server:

```bash
npm run dev
```

The Vite dev server runs by default on http://localhost:5173. The frontend is configured to talk to the backend at `http://localhost:8000` (CORS is allowed for `http://localhost:5173` in the backend).

## Useful commands

- Start backend (reload on change):
  - `uvicorn backend.main:app --reload`
- Start frontend dev server:
  - `npm run dev` (from `Application/frontend`)
- Build frontend for production:
  - `npm run build`

## Docker for beginners

`docker compose up -d db`
`docker compose up -d n8n`
