# Nginx Proxy Manager

Production access must go through Nginx Proxy Manager.

Do not expose the API, PostgreSQL, Redis or Suwayomi ports publicly.

## Proxy Host

Create a Proxy Host with:

```text
Domain Names: reader.hflow.top
Scheme: http
Forward Hostname / IP: panelflow-web
Forward Port: 3000
```

Enable:

- Websockets Support
- Block Common Exploits
- SSL certificate for `reader.hflow.top`
- Force SSL
- HTTP/2 Support

## Docker Network

Nginx Proxy Manager and `panelflow-web` must share the external network:

```text
npm_default
```

Only `panelflow-web` should join that external network.

## Expected Traffic Flow

```text
Browser -> Nginx Proxy Manager -> panelflow-web:3000 -> panelflow-api:8000
```

The browser never talks directly to the API container in production.
