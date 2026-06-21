# PanelFlow / reader.hflow

PanelFlow is a private, self-hosted web reader skeleton for manga, manhwa, webtoons, comics, PDFs, articles and CBZ/ZIP files.

Implemented phases:

- Next.js + TypeScript + Tailwind web dashboard
- FastAPI backend API
- PostgreSQL 16
- Redis 7
- Suwayomi Server
- Local Docker Compose
- Production Docker Compose for Portainer + Nginx Proxy Manager
- Storage writability check for `/data/library`
- Private admin authentication with JWT and password hashing

The production domain is `reader.hflow.top`.

## Current Scope

Implemented API endpoints:

- `GET /health`
- `GET /api/status`
- `GET /api/suwayomi/status`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/logout`

The web dashboard shows:

- API status
- database status
- Redis status
- Suwayomi status
- storage status
- logged-in admin email
- logout action

Not implemented yet:

- public registration
- manga search
- source listing
- chapter reader
- upload system
- PDF reader
- CBZ reader
- PWA offline cache
- AI features
- Kavita
- Caddy

## Local Development With Docker

1. Copy the env example:

```powershell
Copy-Item .env.example .env
```

2. Start the stack:

```powershell
docker compose up --build
```

3. Open the dashboard:

```text
http://localhost:3000
```

4. Check the API directly:

```text
http://localhost:8000/health
http://localhost:8000/api/status
http://localhost:8000/api/suwayomi/status
```

Local Compose exposes only the web and API ports by default. PostgreSQL, Redis and Suwayomi stay on the internal Docker network and can be inspected with `docker compose exec`.

## Production Deployment

Production uses `docker-compose.prod.yml`.

Only `panelflow-web` joins the external `npm_default` network. PostgreSQL, Redis, Suwayomi and the API stay inside `panelflow_internal`.

Nginx Proxy Manager should proxy:

```text
reader.hflow.top -> panelflow-web:3000
```

See:

- [Portainer deployment](docs/DEPLOY_PORTAINER.md)
- [Nginx Proxy Manager](docs/NGINX_PROXY_MANAGER.md)
- [Google Drive storage](docs/GOOGLE_DRIVE_STORAGE.md)
- [Roadmap](docs/ROADMAP.md)

## Environment

Never commit `.env`.

Required production values:

- `POSTGRES_PASSWORD`
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`
- `JWT_SECRET`
- `PANELFLOW_LIBRARY_HOST_PATH`
- `NEXT_PUBLIC_SITE_URL=https://reader.hflow.top`
- `API_INTERNAL_URL=http://api:8000`
- `SUWAYOMI_URL=http://suwayomi:4567`

`ADMIN_PASSWORD` is only used to create the initial admin if that email does not already exist. Existing admin passwords are not overwritten automatically.

## Auth Test Command

With the Docker stack running:

```powershell
docker compose exec api pytest
```

