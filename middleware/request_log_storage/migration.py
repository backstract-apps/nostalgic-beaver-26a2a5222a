from sqlalchemy import text
from database import engine


DDL = """
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


def run() -> None:
    with engine.connect() as conn:
        conn.execute(text(DDL))
        conn.commit()


if __name__ == "__main__":
    run()


