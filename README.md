# obby-stack

The full Obby self-host stack: IRC server, hosted backend, web client.
Run the whole thing or pick parts.

This repository **does not build any image**. Every service is pulled
from Dockerhub. The Dockerfiles live in their per-service repos:

| Image | Source repo |
|-------|-------------|
| `obbyirc/obbyircd` | [ObsidianIRC/ObbyIRCd](https://github.com/ObsidianIRC/ObbyIRCd) |
| `obbyirc/obby-api` | [ObsidianIRC/hosted-backend](https://github.com/ObsidianIRC/hosted-backend) |
| `obbyirc/obby` | [ObsidianIRC/ObsidianIRC](https://github.com/ObsidianIRC/ObsidianIRC) |

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

Bind-mounted under `/data/obby/` by default. Override per-path with
the `*_BIND` env vars. See `.env.example`.

## Extending the IRCd

Drop files in the matching host dir; they're picked up on next restart
(`docker compose restart obbyircd`).

| Type | Host path | In-container | Loaded by |
|------|-----------|--------------|-----------|
| Native C `.c` module | `/data/obby/custom-modules/` | `/home/obbyircd/obby/custom-modules` | compiled to `third/<name>.so` and `loadmodule`-d automatically |
| Server-side JS `.js` | `/data/obby/scripts/` | `conf/scripts` | `obbyscript` (scans dir at boot) |
| Server-side Python `.py` | `/data/obby/scripts/python/` | `conf/scripts/python` | `obbypy` (scans dir at boot) |

## Updating

```bash
docker compose pull && docker compose up -d
```

Each pull resolves the `:latest` tag of every service to whatever the
respective repo's CI most recently published. For reproducible
deployments, pin per-service tags via `OBBYIRCD_IMAGE`,
`OBBY_API_IMAGE`, and `OBBY_WEB_IMAGE` in `.env`.
