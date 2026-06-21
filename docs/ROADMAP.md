# Roadmap

## Phase 1 - Infrastructure Skeleton

Current scope:

- monorepo structure
- Next.js web dashboard
- FastAPI status API
- PostgreSQL 16
- Redis 7
- Suwayomi Server
- local Docker Compose
- production Docker Compose for Portainer and Nginx Proxy Manager
- storage writability checks
- deployment documentation

## Phase 2 - Authentication And Users

Implemented:

- private login
- disabled public registration
- initial admin created from `ADMIN_EMAIL` and `ADMIN_PASSWORD`
- Argon2 password hashing
- JWT access token authentication
- protected dashboard
- logout flow
- basic admin role model

## Phase 3 - Suwayomi Source Integration

Implemented:

- Suwayomi source browsing
- manga/manhwa search
- saving external Suwayomi results into the PanelFlow user library
- duplicate prevention per user/source/external item
- protected source, search and library pages
- backend-only Suwayomi communication

Planned later:

- metadata refresh/sync
- chapters
- favorites
- reading progress

## Phase 4 - Readers

Planned:

- chapter reader
- webtoon mode
- comic page mode
- PDF reader
- CBZ/ZIP reader

## Phase 5 - Uploads And PWA

Planned:

- local upload flow
- library indexing
- PWA installability
- offline cache strategy

## Explicitly Out Of Scope For Phase 3

- chapter reader
- reading progress
- upload system
- PDF reader
- CBZ reader
- PWA offline cache
- offline downloads
- AI features
- Kavita
- Caddy
- payment
- public registration
