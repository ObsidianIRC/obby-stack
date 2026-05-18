# obby-stack

The full Obby self-host stack: IRC server, hosted backend, web client.
Run the whole thing or pick parts.

This repository **does not build any image**. Every service is pulled
from Dockerhub. The Dockerfiles live in their per-service repos:

| Image | Source repo |
|-------|-------------|
| `mattfly/obbyircd` | [ObsidianIRC/ObbyIRCd](https://github.com/ObsidianIRC/ObbyIRCd) |
| `mattfly/obby-api` | [ObsidianIRC/hosted-backend](https://github.com/ObsidianIRC/hosted-backend) |
| `mattfly/obby` | [ObsidianIRC/ObsidianIRC](https://github.com/ObsidianIRC/ObsidianIRC) |

For Kubernetes / Helm, see [obby-helm](https://github.com/ObsidianIRC/obby-helm).

## Quick start

```bash
cp .env.example .env
$EDITOR .env        # set FQDNs, secrets, public IP

# IRC + backend only
docker compose up -d

# everything including the web client
docker compose --profile frontend up -d
```

The whole stack defaults to internal-only ports; expose via Traefik or
your own reverse proxy. Cloak keys, oper password, and TURN secret
are auto-generated on first run if you leave them blank, but they
should be set explicitly for any deployment you care about.

## Profiles

| Profile | Services brought up |
|---------|--------------------|
| (none, default) | `obbyircd`, `obby-api` |
| `frontend` | `obbyircd`, `obby-api`, `obby` (web) |

Set `COMPOSE_PROFILES=frontend` in `.env` to make `frontend` the default.

## Volumes

Named volumes by default. Set the `*_BIND` env vars to absolute host
paths to use bind mounts instead — convenient for off-host backups
and known-location config edits. See `.env.example`.

## Updating

```bash
docker compose pull && docker compose up -d
```

Each pull resolves the `:latest` tag of every service to whatever the
respective repo's CI most recently published. For reproducible
deployments, pin per-service tags via `OBBYIRCD_IMAGE`,
`OBBY_API_IMAGE`, and `OBBY_WEB_IMAGE` in `.env`.
