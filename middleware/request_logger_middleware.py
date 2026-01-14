from fastapi import FastAPI, Request, Response
import time
import logging
import os
import json
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def setup_request_logger_middleware(app: FastAPI) -> FastAPI:
    """
    Setup Request Logger middleware with configurable logging fields
    """

    # Get configuration from environment variables
    log_method = os.getenv("REQUEST_LOG_METHOD", "true").lower() == "true"
    log_status = os.getenv("REQUEST_LOG_STATUS", "true").lower() == "true"
    log_headers = os.getenv("REQUEST_LOG_HEADERS", "false").lower() == "true"
    log_body = os.getenv("REQUEST_LOG_BODY", "false").lower() == "true"
    log_url = os.getenv("REQUEST_LOG_URL", "true").lower() == "true"
    log_response_time = os.getenv("REQUEST_LOG_RESPONSE_TIME", "true").lower() == "true"
    log_query_params = os.getenv("REQUEST_LOG_QUERY_PARAMS", "false").lower() == "true"
    log_level = os.getenv("REQUEST_LOG_LEVEL", "DEBUG").upper()

    # Set log level
    numeric_level = getattr(logging, log_level, logging.DEBUG)
    logger.setLevel(numeric_level)

    @app.middleware("http")
    async def request_logger_middleware(request: Request, call_next):
        # Record start time
        start_time = time.time()

        # Extract request information
        method = request.method
        url = str(request.url)
        path = request.url.path
        query_params = dict(request.query_params)
        headers = dict(request.headers)

        # Get request body if needed
        body = None
        if log_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    body = body_bytes.decode("utf-8")
                    # Try to parse as JSON for better formatting
                    try:
                        body = json.loads(body)
                    except json.JSONDecodeError:
                        pass  # Keep as string if not valid JSON
            except Exception:
                body = "[Unable to read body]"

        # Process request
        response = await call_next(request)

        # Calculate response time
        process_time = time.time() - start_time
        response_time_ms = round(process_time * 1000, 3)

        # Build log message components
        log_parts = []

        if log_method:
            log_parts.append(method)

        if log_url:
            log_parts.append(path)

        if log_status:
            log_parts.append(str(response.status_code))

        if log_response_time:
            log_parts.append(f"{response_time_ms} ms")

        # Add additional info if enabled
        additional_info = []

        if log_query_params and query_params:
            additional_info.append(f"query={query_params}")

        if log_headers and headers:
            # Filter sensitive headers
            filtered_headers = {
                k: v
                for k, v in headers.items()
                if k.lower() not in ["authorization", "cookie", "x-api-key"]
            }
            if filtered_headers:
                additional_info.append(f"headers={filtered_headers}")

        if log_body and body is not None:
            # Truncate large bodies
            body_str = str(body)
            if len(body_str) > 500:
                body_str = body_str[:500] + "... [truncated]"
            additional_info.append(f"body={body_str}")

        # Combine all parts
        log_message = " ".join(log_parts)
        if additional_info:
            log_message += " - " + " | ".join(additional_info)

        # Log the request
        if response.status_code >= 500:
            logger.error(log_message)
        elif response.status_code >= 400:
            logger.warning(log_message)
        else:
            logger.info(log_message)

        # Add response time header
        response.headers["X-Process-Time"] = str(response_time_ms)

        return response

    return app
