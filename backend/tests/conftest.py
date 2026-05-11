from pathlib import Path
import sys

import pytest


# Allow `from app...` imports when running `python -m pytest` from repo root.
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
