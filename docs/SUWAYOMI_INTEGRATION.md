# Suwayomi Integration

Phase 3 adds the first PanelFlow integration with Suwayomi Server.

## Architecture

Suwayomi runs as the private Docker service `panelflow-suwayomi` on the internal PanelFlow network.

The browser does not call Suwayomi directly. Normal source/search requests flow like this:

```text
Browser -> Next.js web -> PanelFlow FastAPI -> Suwayomi GraphQL
```

The protected Suwayomi WebUI uses the same principle:

```text
Browser iframe -> Next.js protected route -> PanelFlow FastAPI admin proxy -> Suwayomi WebUI
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

Admin-only WebUI proxy:

- `GET|POST|PUT|PATCH|DELETE /api/admin/suwayomi/{path}`

The browser-facing page is:

- `/admin/suwayomi`

PanelFlow stores saved external items with:

- `source_type=external_suwayomi`
- `source_id` from the Suwayomi source/extension
- `external_id` from the Suwayomi manga result

The same user cannot add the same external item twice.

## Admin WebUI

Administrators can open `/admin/suwayomi` from the PanelFlow sidebar.

This page embeds Suwayomi's own WebUI through a protected iframe. Use it to install extension repositories, install/remove extensions, and configure Suwayomi settings without exposing Suwayomi directly to the internet.

Security model:

- PanelFlow login is required.
- The user must have `role=admin`.
- `SUWAYOMI_URL` is only used by the backend.
- The proxy only forwards paths under the configured Suwayomi host.
- No new public port, Nginx Proxy Manager host, or subdomain is required.

The page also includes an "Abrir painel Suwayomi protegido" button. Use it if the iframe is blocked by browser behavior or Suwayomi WebUI headers.

## WebUI Subpath Notes

Suwayomi's WebUI was not originally designed specifically for PanelFlow's `/api/admin/suwayomi/` subpath. PanelFlow rewrites common absolute asset paths and routes calls such as `/api/graphql` through the protected proxy, but future WebUI changes may still introduce assets or scripts that assume they are mounted at `/`.

If the WebUI frame loads but styles/scripts are missing:

- Open browser developer tools and check for `404` requests outside `/api/admin/suwayomi/`.
- Confirm the logged-in user is an admin.
- Check API logs with `docker compose logs api`.
- Check Suwayomi logs with `docker compose logs suwayomi`.
- Refresh the page after Suwayomi finishes starting.

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

## Temporary Internal Suwayomi Access Fallback

Do not expose Suwayomi publicly through Nginx Proxy Manager.

Use `/admin/suwayomi` first. Use an SSH tunnel only as a fallback if Suwayomi's WebUI changes in a way that does not work correctly under the protected subpath proxy.

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
