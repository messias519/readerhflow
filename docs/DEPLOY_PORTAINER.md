# Deploy With Portainer

This guide assumes the VPS already has Docker, Portainer, Nginx Proxy Manager and the external Docker network `npm_default`.

## 1. Prepare Storage

Create or mount the production library directory on the host:

```bash
sudo mkdir -p /mnt/gdrive/panelflow/library
sudo chown -R 1000:1000 /mnt/gdrive/panelflow/library
```

If Google Drive is mounted with rclone, make sure the mount exists before starting the stack.

## 2. Create The Stack

In Portainer:

1. Go to **Stacks**.
2. Create a new stack named `panelflow`.
3. Paste the contents of `docker-compose.prod.yml`.
4. Add environment variables from `.env.example`.
5. Set strong production values.
6. Deploy the stack.

Minimum production env:

```env
NEXT_PUBLIC_APP_NAME=PanelFlow
NEXT_PUBLIC_SITE_URL=https://reader.hflow.top
API_INTERNAL_URL=http://api:8000
POSTGRES_DB=panelflow
POSTGRES_USER=panelflow
POSTGRES_PASSWORD=replace-with-a-long-random-password
STORAGE_PATH=/data/library
PANELFLOW_LIBRARY_HOST_PATH=/mnt/gdrive/panelflow/library
REDIS_URL=redis://redis:6379/0
SUWAYOMI_URL=http://suwayomi:4567
CORS_ORIGINS=https://reader.hflow.top
```

## 3. Network Rules

The production compose file connects:

- `panelflow-web` to `panelflow_internal` and `npm_default`
- `panelflow-api` only to `panelflow_internal`
- `panelflow-postgres` only to `panelflow_internal`
- `panelflow-redis` only to `panelflow_internal`
- `panelflow-suwayomi` only to `panelflow_internal`

No internal service ports are published in production.

## 4. Validate

After the stack starts:

1. Confirm all containers are running in Portainer.
2. Configure Nginx Proxy Manager for `reader.hflow.top`.
3. Open `https://reader.hflow.top`.
4. Confirm the dashboard shows API, PostgreSQL, Redis, Suwayomi and storage statuses.
