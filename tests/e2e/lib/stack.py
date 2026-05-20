import json
import os
import secrets
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
COMPOSE_FILE = REPO_ROOT / "compose.yaml"
COMPOSE_OVERRIDE = Path(__file__).resolve().parent.parent / "compose.override.yaml"

_BIND_DIRS = (
    "conf", "data", "logs", "tls",
    "custom-modules", "scripts", "scripts/python",
    "voice-bridge", "api-data", "api-images",
)


class ComposeStack:
    """One isolated obby-stack instance per test."""

    def __init__(self, fixtures: Path | None = None, env_overrides: dict | None = None):
        self.fixtures = fixtures
        self.project = f"obbye2e{secrets.token_hex(4)}"
        self.data_root = Path(tempfile.mkdtemp(prefix="obby-e2e-"))
        for d in _BIND_DIRS:
            (self.data_root / d).mkdir(parents=True, exist_ok=True)
        if fixtures and fixtures.exists():
            for sub in fixtures.iterdir():
                dst = self.data_root / sub.name
                if sub.is_dir():
                    shutil.copytree(sub, dst, dirs_exist_ok=True)
        self.env_file = self.data_root / "test.env"
        self.env = self._build_env(env_overrides or {})
        self._write_env_file()

    def _write_env_file(self):
        lines = [f"{k}={v}" for k, v in self.env.items() if k != "COMPOSE_PROJECT_NAME"]
        self.env_file.write_text("\n".join(lines) + "\n")

    def _build_env(self, overrides):
        env = {
            "COMPOSE_PROJECT_NAME": self.project,
            "SERVER_NAME": "irc.test.local",
            "NETWORK_NAME": "ObbyE2E",
            "ADMIN_EMAIL": "test@test.local",
            "MOTD_TEXT": "test",
            "OPER_NAME": "admin",
            "OPER_PASSWORD": secrets.token_hex(8),
            "SSL_PORT": "6697",
            "WS_PORT": "8080",
            "API_FQDN": "api.test.local",
            "IRC_FQDN": "irc.test.local",
            "WEB_FQDN": "chat.test.local",
            "FILEHOST_URL": "",
            "FILEHOST_PUBLIC_URL": "",
            "RPC_PASSWORD": "",
            "JWT_SECRET": secrets.token_hex(32),
            "IRC_SERVER_KEY": secrets.token_hex(32),
            "VOICE_TURN_SECRET": secrets.token_hex(32),
            "VOICE_PUBLIC_IP": "127.0.0.1",
            "TURN_PORT": "0",
            "VOICE_TURN_REALM": "test",
            "VOICE_MAX_ROOM": "5",
            "UNREALIRCD_API_USERNAME": "admin",
            "CONF_BIND": str(self.data_root / "conf"),
            "DATA_BIND": str(self.data_root / "data"),
            "LOGS_BIND": str(self.data_root / "logs"),
            "TLS_BIND": str(self.data_root / "tls"),
            "CUSTOM_MODULES_BIND": str(self.data_root / "custom-modules"),
            "SCRIPTS_BIND": str(self.data_root / "scripts"),
            "VOICE_BRIDGE_BIND": str(self.data_root / "voice-bridge"),
            "OBBY_API_DATA_BIND": str(self.data_root / "api-data"),
            "OBBY_API_IMAGES_BIND": str(self.data_root / "api-images"),
        }
        env.update(overrides)
        return env

    def _compose(self, *args, check=True, capture=False) -> subprocess.CompletedProcess[str]:
        cmd = [
            "docker", "compose",
            "-f", str(COMPOSE_FILE),
            "-f", str(COMPOSE_OVERRIDE),
            *args,
        ]
        full_env = {**os.environ, **self.env, "E2E_ENV_FILE": str(self.env_file)}
        return subprocess.run(
            cmd, env=full_env, check=check, text=True,
            capture_output=capture,
        )

    def up(self):
        self._compose("up", "-d", "--quiet-pull")
        return self

    def restart(self, service="obbyircd"):
        self._compose("restart", service)

    def down(self):
        try:
            self._compose("down", "-v", "-t", "5", check=False)
        finally:
            shutil.rmtree(self.data_root, ignore_errors=True)

    def port(self, service: str, container_port: int) -> int:
        r = self._compose("port", service, str(container_port), capture=True)
        if r.returncode != 0 or not r.stdout.strip():
            raise RuntimeError(f"no host port for {service}:{container_port}")
        return int(r.stdout.strip().splitlines()[0].rsplit(":", 1)[1])

    def logs(self, service: str) -> str:
        return self._compose("logs", "--no-color", service, capture=True).stdout

    def wait_healthy(self, service="obbyircd", timeout=60):
        deadline = time.time() + timeout
        while time.time() < deadline:
            r = self._compose("ps", "--format", "json", service, capture=True)
            for line in r.stdout.splitlines():
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("Health") == "healthy":
                    return
            time.sleep(1)
        raise TimeoutError(f"{service} never became healthy: {self.logs(service)[-2000:]}")

    def read_container_file(self, service: str, path: str) -> str:
        r = self._compose("exec", "-T", service, "cat", path, capture=True)
        return r.stdout

    def wait_log(self, service: str, needle: str, timeout=30):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if needle in self.logs(service):
                return
            time.sleep(0.5)
        raise TimeoutError(f"never saw {needle!r} in {service} logs")
