# Observability

AlienCommons uses Grafana Alloy to discover the current Docker Compose project's
containers and forward their logs to Loki. Grafana reads Loki through a
provisioned data source.

The configuration is shared by all environments. Compose supplies only the
environment-specific values:

- `ALLOY_COMPOSE_PROJECT` limits discovery to the matching Compose project.
- `ALLOY_ENVIRONMENT` becomes the `environment` log label.
- `LOKI_RETENTION_PERIOD` controls both retention and the maximum query window.

Alloy stores Docker read positions under `/var/lib/alloy/data`, Loki stores its
WAL, indexes, chunks, and compactor state under `/loki`, and Grafana stores its
database and plugins under `/var/lib/grafana`. Keep each host-side directory
persistent across container replacement.

Before staging or production deployment, define `GRAFANA_ADMIN_USER` and a
strong `GRAFANA_ADMIN_PASSWORD` in the corresponding ignored `env/.env.*` file.
The password is required for non-development Compose configuration and startup;
development defaults to `admin`/`admin`. Do not expose Grafana directly to the
internet; staging is routed through Traefik and production binds only to
loopback for access through an authenticated tunnel or proxy.

Grafana's admin environment variables only initialize a new database. After
deploying this change to an environment with an existing Grafana database, use
`grafana cli admin reset-admin-password` inside the container to rotate the
existing admin password as well.

To inspect logs in Grafana Explore, filter on the stable labels
`environment`, `service_name`, and `compose_project`. The `container` label can
distinguish replicas of the same service.
