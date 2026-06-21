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
- Initial Suwayomi integration for sources, search and saved library items

The production domain is `reader.hflow.top`.

## Current Scope

Implemented API endpoints:

- `GET /health`
- `GET /api/status`
- `GET /api/suwayomi/status`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/logout`
- `GET /api/sources`
- `GET /api/sources/{source_id}`
- `GET /api/search?source_id=...&query=...`
- `POST /api/library/external`
- `GET /api/library`
- `GET /api/library/{item_id}`
- `GET|POST|PUT|PATCH|DELETE /api/admin/suwayomi/{path}`

The web dashboard shows:

- API status
- database status
- Redis status
- Suwayomi status
- storage status
- logged-in admin email
- logout action
- source list
- source search
- user library
- protected admin access to the internal Suwayomi WebUI

Not implemented yet:

- public registration
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

## Suwayomi Integration

PanelFlow uses Suwayomi as an internal manga/manhwa source engine. The browser never talks to Suwayomi directly; Next.js calls the PanelFlow API, and the API calls Suwayomi through `SUWAYOMI_URL` inside Docker.

Source browsing and search use Suwayomi's GraphQL API. Results added to the PanelFlow library are stored in PostgreSQL with `source_type=external_suwayomi`, and duplicate saves are prevented per user by `source_id + external_id`.

Admins can open `/admin/suwayomi` to access Suwayomi's WebUI through a protected PanelFlow proxy. Suwayomi is still not exposed directly to the public internet.

See [Suwayomi integration](docs/SUWAYOMI_INTEGRATION.md).

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
- [Suwayomi integration](docs/SUWAYOMI_INTEGRATION.md)
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

