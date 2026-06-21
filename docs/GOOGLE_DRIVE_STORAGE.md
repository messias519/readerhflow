# Google Drive Storage

PanelFlow does not implement Google OAuth or rclone authentication.

The app only checks whether `STORAGE_PATH` exists and is writable from inside the API container.

## Container Path

The API expects library storage at:

```text
/data/library
```

## Production Bind Mount

On the VPS, mount Google Drive with rclone or another host-level method, then bind that host path into the API container:

```env
PANELFLOW_LIBRARY_HOST_PATH=/mnt/gdrive/panelflow/library
STORAGE_PATH=/data/library
```

The production compose file maps:

```text
${PANELFLOW_LIBRARY_HOST_PATH}:/data/library
```

## Validation

The `/api/status` endpoint checks:

- path exists
- path is a directory
- path is writable
- a small temporary write/delete operation succeeds

If storage is unavailable, the dashboard reports the storage service as offline or degraded.
