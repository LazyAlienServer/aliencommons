# Traefik

Traefik terminates HTTPS for the staging and production Compose projects. All
public services and Traefik join the external `aliencommons-proxy` Docker
network; application-internal traffic remains on each project's default
network.

## First-time setup

1. Copy `env/.env.proxy.example` to `env/.env.proxy` and set an email address
   monitored by the operators.
2. Point the public DNS records at the proxy host and allow inbound TCP ports
   80 and 443. Port 80 must remain reachable for the Let's Encrypt HTTP-01
   challenge and redirects all other requests to HTTPS.
3. Run `make proxy-check`, then `make proxy-up` before starting staging or
   production.

Certificates are stored in the `aliencommons-proxy_letsencrypt` Docker volume,
which survives container recreation and `make proxy-down`. Back up this volume
with the rest of the host's persistent deployment data.

The dashboard is disabled. Traefik emits JSON application and access logs to
stdout, and its Docker socket mount is read-only. Shared TLS and response-header
policy lives under `infra/traefik/dynamic/`.
