# Suwayomi Integration

Phase 3 adds the first PanelFlow integration with Suwayomi Server.

## Architecture

Suwayomi runs as the private Docker service `panelflow-suwayomi` on the internal PanelFlow network.

The browser does not call Suwayomi directly. Requests flow like this:

```text
Browser -> Next.js web -> PanelFlow FastAPI -> Suwayomi GraphQL
```

The backend reads the Suwayomi base URL from `SUWAYOMI_URL`, usually:

```text
http://suwayomi:4567
```

or, in some compose setups:

```text
http://panelflow-suwayomi:4567
```

Only the web container is attached to the external Nginx Proxy Manager network in production. Suwayomi remains private.

## Implemented Endpoints

All endpoints below require PanelFlow authentication:

- `GET /api/sources`
- `GET /api/sources/{source_id}`
- `GET /api/search?source_id=...&query=...`
- `POST /api/library/external`
- `GET /api/library`
- `GET /api/library/{item_id}`

PanelFlow stores saved external items with:

- `source_type=external_suwayomi`
- `source_id` from the Suwayomi source/extension
- `external_id` from the Suwayomi manga result

The same user cannot add the same external item twice.

## Diagnosing Empty Sources

If `/api/sources` returns an empty list:

1. Confirm the Suwayomi container is running:

```powershell
docker compose ps suwayomi
```

2. Check the PanelFlow status endpoint:

```powershell
curl http://localhost:8000/api/status
```

3. Check Suwayomi logs:

```powershell
docker compose logs suwayomi
```

4. Confirm extensions are installed inside Suwayomi. A fresh Suwayomi install may have no usable sources until extension repositories and extensions are configured.

## Diagnosing Errors

If `/api/sources` returns an error:

- Check `SUWAYOMI_URL` in `.env` or Portainer environment variables.
- Confirm the API container can resolve the Suwayomi service name.
- Check whether Suwayomi is still starting up.
- Inspect `docker compose logs api` and `docker compose logs suwayomi`.

PanelFlow intentionally returns friendly structured errors instead of raw Suwayomi stack traces.

## Temporary Internal Suwayomi Access

Do not expose Suwayomi publicly through Nginx Proxy Manager.

For temporary local access from the VPS, use an SSH tunnel:

```powershell
ssh -L 4567:localhost:4567 user@your-vps
```

If Suwayomi is not bound on the host, use a short-lived local-only port mapping in a maintenance compose override, or access it from inside the Docker network with a temporary helper container. Remove the mapping after installing/configuring extensions.

In production, the intended public entrypoint remains:

```text
reader.hflow.top -> panelflow-web:3000
```

## Current Limits

Phase 3 does not implement chapter readers, reading progress, downloads, uploads, PDF, CBZ/ZIP, offline PWA behavior, Kavita, or a custom extension system.
