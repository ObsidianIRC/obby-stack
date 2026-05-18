import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.stack import ComposeStack

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def stack_factory():
    spawned: list[ComposeStack] = []

    def make(fixtures_subdir: str | None = None, **env_overrides):
        f = (FIXTURES / fixtures_subdir) if fixtures_subdir else None
        s = ComposeStack(fixtures=f, env_overrides=env_overrides).up()
        spawned.append(s)
        s.wait_healthy()
        return s

    yield make
    for s in spawned:
        s.down()
