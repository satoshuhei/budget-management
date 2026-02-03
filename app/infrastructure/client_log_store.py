from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.settings import settings


def append_client_log(payload: dict[str, Any]) -> None:
    log_path = Path(settings.client_log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False))
        handle.write("\n")
