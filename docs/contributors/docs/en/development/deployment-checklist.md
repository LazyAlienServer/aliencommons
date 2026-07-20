# Deployment Checklist

## Configure Traefik

Before starting Traefik on a staging or production host, create its local
environment file from the tracked example:

```bash
cp env/.env.proxy.example env/.env.proxy
```

Open `env/.env.proxy` and replace `TRAEFIK_ACME_EMAIL` with a real operations
email address. The file is intentionally ignored by Git and must be configured
separately on every proxy host.

Confirm that the public DNS records point to the proxy host and that inbound TCP
ports 80 and 443 are reachable. Port 80 is required by the Let's Encrypt HTTP-01
challenge.

Validate and start the proxy before bringing up staging or production:

```bash
make proxy-check
make proxy-up
```

Traefik stores issued certificates in the
`aliencommons-proxy_letsencrypt` Docker volume. Include this volume in the
host's persistent-data backup plan.
