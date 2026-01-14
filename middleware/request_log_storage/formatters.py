import os
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class LogFormat(str, Enum):
    APACHE = "Apache"
    COLOR = "Color"
    MINIMAL = "Minimal"


def normalize_log_format_from_env(value: Optional[str] = None) -> LogFormat:
    """
    Resolve REQUEST_LOG_FORMAT from env or provided value to a LogFormat enum.
    Accepted values (case-insensitive): 'Apache', 'Color', 'Minimal'
    """
    raw = (value or os.getenv("REQUEST_LOG_FORMAT") or "Apache").strip().lower()
    if raw in {"apache", "apache-style", "apache_style"}:
        return LogFormat.APACHE
    if raw in {"color", "color-coded", "color_coded", "colour", "colour-coded"}:
        return LogFormat.COLOR
    if raw in {"minimal", "min"}:
        return LogFormat.MINIMAL
    # Default
    return LogFormat.APACHE


def _color(text: str, code: int) -> str:
    return f"\033[{code}m{text}\033[0m"


def _status_color(status_code: int) -> int:
    if 200 <= status_code < 300:
        return 32  # green
    if 300 <= status_code < 400:
        return 36  # cyan
    if 400 <= status_code < 500:
        return 33  # yellow
    return 31  # red


def _fmt_len(content_length: Optional[int]) -> str:
    try:
        return str(int(content_length)) if content_length is not None else "-"
    except Exception:
        return "-"


def format_apache_style(data: Dict[str, Any]) -> str:
    """
    Example:
    ::1 - - [05/Sep/2025:13:30:25 +0000] "GET / HTTP/1.1" 200 "-" "Mozilla/5.0"
    """
    client_ip = data.get("client_ip") or "-"
    ident = "-"
    user = "-"
    ts = datetime.utcnow().strftime("%d/%b/%Y:%H:%M:%S +0000")
    method = data.get("method") or "-"
    path = data.get("path") or "-"
    http_version = data.get("http_version") or "HTTP/1.1"
    status = data.get("status_code") or 0
    referer = data.get("referer") or "-"
    user_agent = data.get("user_agent") or "-"
    return f'{client_ip} {ident} {user} [{ts}] "{method} {path} {http_version}" {status} "{referer}" "{user_agent}"'


def format_color_coded(data: Dict[str, Any]) -> str:
    """
    Example (colors embedded via ANSI codes):
    GET / 200 5.123 ms - 11
    """
    method = data.get("method") or "-"
    path = data.get("path") or "-"
    status = int(data.get("status_code") or 0)
    duration_ms = float(data.get("duration_ms") or 0.0)
    content_length = _fmt_len(data.get("content_length"))

    colored_method = _color(method, 37)  # white/bright
    colored_status = _color(str(status), _status_color(status))
    colored_time = _color(f"{duration_ms:.3f} ms", 35)  # magenta

    return f"{colored_method} {path} {colored_status} {colored_time} - {content_length}"


def format_minimal(data: Dict[str, Any]) -> str:
    """
    Example:
    GET / 200 - 11 - 5.123 ms
    """
    method = data.get("method") or "-"
    path = data.get("path") or "-"
    status = int(data.get("status_code") or 0)
    content_length = _fmt_len(data.get("content_length"))
    duration_ms = float(data.get("duration_ms") or 0.0)
    return f"{method} {path} {status} - {content_length} - {duration_ms:.3f} ms"


def format_log_entry(data: Dict[str, Any], style: Optional[LogFormat | str] = None) -> str:
    """
    Create a formatted log string using the requested style.
    """
    lf = normalize_log_format_from_env(str(style) if isinstance(style, str) else None) if style else normalize_log_format_from_env()
    if lf == LogFormat.APACHE:
        return format_apache_style(data)
    if lf == LogFormat.COLOR:
        return format_color_coded(data)
    return format_minimal(data)

