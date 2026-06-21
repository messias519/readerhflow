# PanelFlow / Reader.hflow - Codex Instructions

## Project goal

Build a private self-hosted web/PWA reader for manga, manhwa, webtoons, comics, PDFs, articles and CBZ/ZIP files.

The app will replace mobile manga apps by providing a single browser-based experience across desktop, tablet and phone.

Production domain:

reader.hflow.top

## Infrastructure context

The production VPS already has:

- Docker
- Portainer
- Nginx Proxy Manager
- domain hflow.top
- external Docker network: npm_default
- Google Drive mounted through rclone or a future rclone mount

Do not use Caddy.
Do not use Kavita.
Do not expose internal services publicly.

Only the web container should connect to the external Nginx Proxy Manager network.

Internal services must remain inside the PanelFlow internal Docker network.

## Tech stack

Use:

- Next.js + TypeScript for the web app
- Tailwind CSS for styling
- FastAPI + Python for the backend API
- PostgreSQL 16 for persistent data
- Redis 7 for cache/queue
- Suwayomi Server as the external manga/manhwa source engine
- Docker Compose for local and production deployment

## Storage

Local uploaded files must be stored inside the API container at:

/data/library

In production this path will be bind-mounted to a Google Drive path on the host, for example:

/mnt/gdrive/panelflow/library:/data/library

Do not implement Google OAuth or rclone authentication inside the app.

The app should only check whether STORAGE_PATH exists and is writable.

## Security rules

- Do not hardcode secrets.
- Use .env.example only.
- Never expose PostgreSQL, Redis, Suwayomi or API ports publicly in production.
- Production access must go through Nginx Proxy Manager.
- Public registration must be disabled when auth is implemented.
- Authentication is not part of Phase 1.

## MVP Phase 1 scope

Implement only the infrastructure skeleton.

Create:

- monorepo structure
- apps/web
- apps/api
- Dockerfiles
- docker-compose.yml for local development
- docker-compose.prod.yml for Portainer/Nginx Proxy Manager deployment
- .env.example
- README.md
- docs/DEPLOY_PORTAINER.md
- docs/NGINX_PROXY_MANAGER.md
- docs/GOOGLE_DRIVE_STORAGE.md
- docs/ROADMAP.md

API endpoints:

- GET /health
- GET /api/status
- GET /api/suwayomi/status

The API status endpoint must check:

- app status
- database connectivity
- Redis connectivity
- Suwayomi connectivity
- STORAGE_PATH existence and writability

The web app must show:

- dark responsive dashboard placeholder
- API status
- database status
- Redis status
- Suwayomi status
- storage status

## Do not implement in Phase 1

Do not implement:

- authentication
- manga search
- source listing
- chapter reader
- upload system
- PDF reader
- CBZ reader
- PWA offline cache
- AI features
- Kavita integration
- Caddy
- payment
- public registration

## Production deployment assumptions

Production domain:

reader.hflow.top

Nginx Proxy Manager should proxy:

reader.hflow.top -> panelflow-web:3000

External Docker network:

npm_default

Only panelflow-web connects to npm_default.

All other services must stay private.

## Development behavior

Keep changes small and incremental.

Always keep Docker Compose working.

Prefer simple, production-oriented code.

Add clear documentation.

After implementing Phase 1, provide exact commands to test locally and exact steps for Portainer deployment.
