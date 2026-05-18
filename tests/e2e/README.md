# obby-stack e2e

Spins up the compose stack in isolation per test, runs assertions
against a live IRCd / API.

## Run locally

```
cd tests/e2e
uv venv && source .venv/bin/activate
uv pip install -e .
pytest -v
```

Requires Docker. Each test starts its own compose project under a
random `COMPOSE_PROJECT_NAME`, mounts an ephemeral `/tmp/obby-e2e-*`
as data root, and tears down on exit.

## Adding a scenario

- Drop a fixture tree under `fixtures/<name>/` mirroring
  `custom-modules/`, `scripts/`, `scripts/python/`.
- Pass the dir name to `stack_factory("name")`.

## Layout

- `lib/stack.py` — compose lifecycle wrapper
- `lib/irc.py` — minimal async IRC over TLS
- `compose.override.yaml` — ephemeral ports, no Traefik labels
- `fixtures/` — sample drop-in modules per scenario
