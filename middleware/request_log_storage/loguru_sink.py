import os
import re
from typing import Any, Dict

from loguru import logger

from .repository import log_raw_message_to_db, ensure_table_exists

_SINK_INSTALLED = False


def _parse_loguru_message(message: str) -> Dict[str, Any]:
    """
    Parse the log message emitted by the Prometheus middleware in main.py, e.g.:
    "➡️ ✅ GET /path Status: 200 response:<...> ⏱️ Time: 12.34ms"
    """
    data: Dict[str, Any] = {}
    try:
        m = re.search(r"(GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD)\s+(\S+)", message)
        if m:
            data["method"] = m.group(1)
            data["path"] = m.group(2)
        s = re.search(r"Status:\s+(\d{3})", message)
        if s:
            data["status_code"] = int(s.group(1))
        t = re.search(r"Time:\s*([0-9]+(?:\.[0-9]+)?)ms", message)
        if t:
            data["duration_ms"] = float(t.group(1))
    except Exception:
        pass
    return data


def _sink(message):
    try:
        text = message.strip() if isinstance(message, str) else str(message)
        parsed = _parse_loguru_message(text)
        if parsed:
            # Tag style to indicate source
            parsed.setdefault("style", "App")
            log_raw_message_to_db(text, parsed)
    except Exception:
        # Swallow all exceptions to avoid breaking logging
        return


def install_loguru_db_sink() -> None:
    global _SINK_INSTALLED
    if _SINK_INSTALLED:
        return
    enabled = (os.getenv("REQUEST_LOG_DB_ENABLED", "true") or "true").strip().lower() == "true"
    if not enabled:
        return
    ensure_table_exists()
    # Add a level threshold of INFO to match the app's typical request logs
    logger.add(_sink, level="INFO")
    _SINK_INSTALLED = True

