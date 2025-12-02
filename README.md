# Yelp Geo-Distributed Discovery

FastAPI + React application demonstrating geo-distributed discovery on the Yelp dataset.
The system highlights sharded MongoDB reads/writes, transactional review inserts, and semantic
search backed by Weaviate and Ollama embeddings.

## Architecture at a Glance

- **MongoDB Cluster** – Sharded by U.S. region for businesses/reviews with replica sets per shard.
- **FastAPI Backend** (`backend/`) – Consolidated API exposing:
  - `/businesses`, `/reviews`, `/users` resource endpoints
  - Discovery routes (`/search/location`, `/business/{id}`, `/business/{id}/reviews`)
  - Semantic search (`/search/semantic`) combining geo filters + vector search
  - Custom dark-themed Swagger UI at `http://localhost:8000/docs`
- **React Frontend** (`frontend/`) – Vite app that mirrors the dark UI and consumes the APIs.
- **Vector Layer** – Weaviate stores review embeddings generated through Ollama (`all-minilm`).
- **Archive** (`archive/legacy_tools/`) – Legacy scripts and notebooks retained for reference.

## Getting Started

1. **Install prerequisites**

   - Docker Desktop (for the Mongo + Weaviate + Ollama compose stack)
   - Python 3.11+ (project uses 3.13)
   - Node.js 18+ or Bun

2. **Start data services**

   ```bash
   cd DDS
   docker-compose up -d
   ```

3. **Run the backend**

   ```bash
   cd DDS
   python3 -m venv ../venv
   source ../venv/bin/activate
   pip install -r requirements.txt
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

   - Swagger UI: `http://localhost:8000/docs`
   - OpenAPI schema: `http://localhost:8000/openapi.json`

4. **Run the frontend**
   ```bash
   cd DDS/frontend
   npm install
   npm run dev -- --host 0.0.0.0 --port 5173
   ```
   Visit `http://localhost:5173` and try a semantic search (e.g., lat `34.42`, long `-119.7`, radius `5000`).

## Repository Layout

```
backend/           FastAPI app (routers, models, config, static docs theme)
frontend/          Vite + React client
archive/           Legacy scripts/notebooks retained for reference
docker-compose.yml Mongo + Weaviate + Ollama stack
backend/README.md  Backend feature overview
backend/TESTING.md Testing guide (Swagger, curl, Postman examples)
```

## Testing & Validation

- See [`backend/TESTING.md`](backend/TESTING.md) for curl examples, Swagger usage, and validation tips.
- Semantic backfill tooling: [`backfill_weaviate.py`](backfill_weaviate.py) populates Weaviate from Mongo.
- Archive scripts (`archive/legacy_tools/`) contain historical data migration helpers if needed.

## Additional Notes

- The unified backend under `backend/` is the single source of truth (legacy duplicates were removed).
- Swagger UI styling lives under [`backend/static/docs.css`](backend/static/docs.css) to match the frontend look.
- Adjust connection details in [`backend/config.py`](backend/config.py) if your cluster differs from the local compose defaults.
