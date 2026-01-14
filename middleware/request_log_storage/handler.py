import logging
import os
import re
from typing import Any, Dict, Optional

from .repository import log_raw_message_to_db, ensure_table_exists

_INSTALLED = False


def _parse_message(msg: str) -> Dict[str, Any]:
    """
    Best-effort parsing to extract method, path, status_code, duration_ms and content_length
    from various formats, including the project's default middleware and our formatters.
    """
    result: Dict[str, Any] = {}
    try:
        # Method and path (start of line)
        m = re.search(r"^(GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD)\s+(\S+)", msg)
        if m:
            result["method"] = m.group(1)
            result["path"] = m.group(2)
        # Status code
        s = re.search(r"\s(\d{3})(\s|$)", msg)
        if s:
            result["status_code"] = int(s.group(1))
        # Duration in ms
        d = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*ms", msg)
        if d:
            result["duration_ms"] = float(d.group(1))
        # Content length (trailing " - N" or " - N " variants)
        c = re.search(r"-\s*([0-9]{1,12})(\s|$)", msg)
        if c:
            try:
                result["content_length"] = int(c.group(1))
            except Exception:
                pass
    except Exception:
        pass
    return result


class RequestLogDBHandler(logging.Handler):
    """
    Logging handler that persists request logger lines into SQLite.
    Attaches to logger name 'middleware.request_logger_middleware' by default.
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = record.getMessage()
            parsed = _parse_message(msg)
            # Add level/logger context for potential future use
            if record.name:
                parsed.setdefault("logger", record.name)
            if record.levelname:
                parsed.setdefault("level", record.levelname)
            log_raw_message_to_db(msg, parsed)
        except Exception:
            # Never raise from logging handler
            return


def install_request_log_db_handler(logger_name: str = "middleware.request_logger_middleware") -> None:
    """
    Install the handler once. Controlled by env REQUEST_LOG_DB_ENABLED (default: true).
    """
    global _INSTALLED
    if _INSTALLED:
        return
    enabled = (os.getenv("REQUEST_LOG_DB_ENABLED", "true") or "true").strip().lower() == "true"
    if not enabled:
        return
    ensure_table_exists()
    handler = RequestLogDBHandler()
    handler.setLevel(logging.DEBUG)
    logging.getLogger(logger_name).addHandler(handler)
    _INSTALLED = True

