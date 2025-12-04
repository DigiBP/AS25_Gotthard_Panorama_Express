n8n local Docker Compose (Postgres)

This compose file launches a local n8n instance backed by Postgres for persistence.

Files
- `docker-compose.n8n.yml` - Docker Compose file for n8n and postgres.
- `.env.n8n` - Example environment variables. Copy to `.env.n8n` or to `.env` and edit.

Quick start
1. From `Application/` directory, copy the env file and edit secrets:
   - On Windows (cmd.exe):
     copy .env.n8n .env
   - Edit `.env` and set `DB_PASSWORD`, `N8N_PASSWORD`, and `N8N_JWT_SECRET` to secure values.

2. Start services:
   docker compose -f docker-compose.n8n.yml up -d

3. Open n8n in your browser: http://localhost:5678

Stopping
- docker compose -f docker-compose.n8n.yml down -v

Notes
- The compose uses the official n8n image and Postgres 15.
- Basic auth is enabled; change credentials in the `.env` file.
- For production deployments, consult n8n docs for advanced security, TLS, and scaling.
