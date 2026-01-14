import json
from contextlib import contextmanager
from typing import Any, Dict, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from .formatters import LogFormat, format_log_entry, normalize_log_format_from_env


@contextmanager
def get_db_session() -> Session:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def ensure_table_exists() -> None:
    create_sql = """
CREATE TABLE IF NOT EXISTS mayson_request_logger (
    
    
    id BIGSERIAL PRIMARY KEY,
    ts_utc TIMESTAMPTZ NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
    

    method TEXT,
    path TEXT,
    status_code INTEGER,
    
    
    duration_ms DOUBLE PRECISION,
    
    
    client_ip TEXT,
    user_agent TEXT,
    content_length INTEGER,
    style TEXT,
    message TEXT


);

"""

    with engine.connect() as conn:
        conn.execute(text(create_sql))
        conn.commit()


def log_request_to_db(
    data: Dict[str, Any],
    style: Optional[LogFormat | str] = None,
    session: Optional[Session] = None,
) -> int:

    resolved_style = normalize_log_format_from_env(str(style) if isinstance(style, str) else None) if style else normalize_log_format_from_env()
    message = format_log_entry(data, resolved_style.value)

    payload = {
        "method": data.get("method"),
        "path": data.get("path"),
        "status_code": int(data.get("status_code") or 0),
        "duration_ms": float(data.get("duration_ms") or 0.0),
        "client_ip": data.get("client_ip"),
        "user_agent": data.get("user_agent"),
        "content_length": int(data.get("content_length")) if data.get("content_length") is not None else None,
        "style": resolved_style.value,
        "message": message,
    }

    sql = text(
        """
        INSERT INTO request_logs (
            method, path, status_code, duration_ms, client_ip, user_agent,
            content_length, style, message
        ) VALUES (
            :method, :path, :status_code, :duration_ms, :client_ip, :user_agent,
            :content_length, :style, :message
        )
        """
    )

    if session is None:
        with get_db_session() as db:
            result = db.execute(sql, payload)
            rowid = int(result.lastrowid) if hasattr(result, "lastrowid") and result.lastrowid is not None else 0
            return rowid

    result = session.execute(sql, payload)
    return int(result.lastrowid) if hasattr(result, "lastrowid") and result.lastrowid is not None else 0


def log_raw_message_to_db(
    message: str,
    fields: Optional[Dict[str, Any]] = None,
    session: Optional[Session] = None,
) -> int:

    ensure_table_exists()
    payload = {
        "method": (fields or {}).get("method"),
        "path": (fields or {}).get("path"),
        "status_code": int((fields or {}).get("status_code") or 0) if (fields or {}).get("status_code") is not None else None,
        "duration_ms": float((fields or {}).get("duration_ms") or 0.0) if (fields or {}).get("duration_ms") is not None else None,
        "client_ip": (fields or {}).get("client_ip"),
        "user_agent": (fields or {}).get("user_agent"),
        "content_length": int((fields or {}).get("content_length")) if (fields or {}).get("content_length") is not None else None,
        "style": (fields or {}).get("style"),
        "message": message,
    }
    sql = text(
        """
        INSERT INTO mayson_request_logger (
            method, path, status_code, duration_ms, client_ip, user_agent,
            content_length, style, message
        ) VALUES (
            :method, :path, :status_code, :duration_ms, :client_ip, :user_agent,
            :content_length, :style, :message
        )
        
        RETURNING id
        
        """
    )

    if session is None:
        with get_db_session() as db:
            try:
                result = db.execute(sql, payload)
                
                inserted_id = result.scalar() if hasattr(result, "scalar") else None
                return int(inserted_id) if inserted_id is not None else 0
                

            except Exception:
                # Never fail application due to logging insert
                return 0
    try:
        result = session.execute(sql, payload)
        
        inserted_id = result.scalar() if hasattr(result, "scalar") else None
        return int(inserted_id) if inserted_id is not None else 0
        
    
    except Exception:
        return 0

