"""
Auto-generated middleware file
Contains middleware functions and groups defined in the collection
"""

import os
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, List, Dict, Any
import jwt
from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# Middleware: CORS Middleware
# Slug: cors_middleware
async def cors_middleware(request: Request) -> Dict[str, Any]:
    """
    CORS Middleware
    Generated from middleware ID: mid_e3da11bc2af542e4b8cc43029816aa8a
    """
    try:

        def setup_cors_middleware(app: FastAPI):
            """
            Setup CORS middleware with configuration from environment variables
            """

            # Get CORS configuration from environment variables
            origins = os.getenv("CORS_ORIGIN", "*").split(",")
            methods = os.getenv("CORS_METHOD", "GET,POST,PUT,DELETE,OPTIONS").split(",")
            allowed_headers = os.getenv("CORS_HEADERS", "*").split(",")
            exposed_headers = (
                os.getenv("CORS_EXPOSED_HEADERS", "").split(",")
                if os.getenv("CORS_EXPOSED_HEADERS")
                else []
            )
            credentials = os.getenv("CORS_CREDENTIALS", "false").lower() == "true"
            max_age = int(os.getenv("CORS_MAX_AGE", "3600"))

            # Add CORS middleware
            app.add_middleware(
                CORSMiddleware,
                allow_origins=origins,
                allow_credentials=credentials,
                allow_methods=methods,
                allow_headers=allowed_headers,
                expose_headers=exposed_headers,
                max_age=max_age,
            )

            return app

        return {}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Middleware error: {str(e)}")


# Middleware: Request Logger Middleware
# Slug: request_logger_middleware
async def request_logger_middleware(request: Request) -> Dict[str, Any]:
    """
    Request Logger Middleware
    Generated from middleware ID: mid_7ce5f9881ddf42f39244146c7808b9f2
    """
    try:
        import os
        import time
        import logging
        import json
        from fastapi import FastAPI, Request, Response
        from typing import Dict, Any

        # Configure logging
        logging.basicConfig(level=logging.INFO)
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
            log_response_time = (
                os.getenv("REQUEST_LOG_RESPONSE_TIME", "true").lower() == "true"
            )
            log_query_params = (
                os.getenv("REQUEST_LOG_QUERY_PARAMS", "false").lower() == "true"
            )
            log_level = os.getenv("REQUEST_LOG_LEVEL", "INFO").upper()

            # Set log level
            numeric_level = getattr(logging, log_level, logging.INFO)
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

        return {}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Middleware error: {str(e)}")


# Middleware: Security Headers Middleware
# Slug: security_headers_middleware
async def security_headers_middleware(request: Request) -> Dict[str, Any]:
    """
    Security Headers Middleware
    Generated from middleware ID: mid_af40299a537f49f286b4fe34b5c4ea60
    """
    try:
        from fastapi import FastAPI, Request, Response
        import os
        from typing import Optional, List
        from urllib.parse import urlparse

        def setup_security_headers_middleware(app: FastAPI) -> FastAPI:
            """
            Setup Security Headers middleware with configurable security headers, HTTPS enforcement, and trusted host validation
            """

            # Get configuration from environment variables
            enable_strict_transport_security = (
                os.getenv("SECURITY_HEADERS_STRICT_TRANSPORT_SECURITY", "false").lower()
                == "true"
            )
            enable_x_frame_options = (
                os.getenv("SECURITY_HEADERS_X_FRAME_OPTIONS", "false").lower() == "true"
            )
            enable_x_content_type_options = (
                os.getenv("SECURITY_HEADERS_X_CONTENT_TYPE_OPTIONS", "false").lower()
                == "true"
            )
            enable_content_security_policy = (
                os.getenv("SECURITY_HEADERS_CONTENT_SECURITY_POLICY", "false").lower()
                == "true"
            )
            enable_referer_policy = (
                os.getenv("SECURITY_HEADERS_REFERER_POLICY", "false").lower() == "true"
            )

            # HTTPS enforcement
            force_https = (
                os.getenv("SECURITY_HEADERS_FORCE_HTTPS", "false").lower() == "true"
            )

            # Trusted host validation
            trusted_host_enabled = (
                os.getenv("SECURITY_HEADERS_TRUSTED_HOST", "false").lower() == "true"
            )
            trusted_hosts = os.getenv("SECURITY_HEADERS_TRUSTED_HOST_LIST", "").split(
                ","
            )
            trusted_hosts = [host.strip() for host in trusted_hosts if host.strip()]

            # Security header values (with defaults). If env is unset or blank/whitespace, use defaults.
            strict_transport_security_value = (
                os.getenv("SECURITY_HEADERS_HSTS_VALUE") or ""
            ).strip() or "max-age=31536000; includeSubDomains"
            x_frame_options_value = (
                os.getenv("SECURITY_HEADERS_X_FRAME_OPTIONS_VALUE") or ""
            ).strip() or "DENY"
            x_content_type_options_value = (
                os.getenv("SECURITY_HEADERS_X_CONTENT_TYPE_OPTIONS_VALUE") or ""
            ).strip() or "nosniff"
            content_security_policy_value = (
                os.getenv("SECURITY_HEADERS_CSP_VALUE") or ""
            ).strip() or "default-src 'self'"
            referer_policy_value = (
                os.getenv("SECURITY_HEADERS_REFERER_POLICY_VALUE") or ""
            ).strip() or "strict-origin-when-cross-origin"

            @app.middleware("http")
            async def security_headers_middleware(request: Request, call_next):
                # Trusted host validation
                if trusted_host_enabled and trusted_hosts:
                    host = request.headers.get("Host", "")
                    # Remove port if present
                    host_without_port = host.split(":")[0] if ":" in host else host

                    # Check if host is in trusted list
                    if host_without_port not in trusted_hosts:
                        return Response(content="Invalid Host header", status_code=400)

                # Force HTTPS redirect
                if force_https:
                    # Check if request is HTTP (not HTTPS)
                    url = str(request.url)
                    if url.startswith("http://"):
                        # Get the HTTPS URL
                        https_url = url.replace("http://", "https://", 1)
                        return Response(
                            status_code=301, headers={"Location": https_url}
                        )

                # Process request
                response = await call_next(request)

                # Add security headers based on configuration
                if enable_strict_transport_security:
                    response.headers["Strict-Transport-Security"] = (
                        strict_transport_security_value
                    )

                if enable_x_frame_options:
                    response.headers["X-Frame-Options"] = x_frame_options_value

                if enable_x_content_type_options:
                    response.headers["X-Content-Type-Options"] = (
                        x_content_type_options_value
                    )

                if enable_content_security_policy:
                    response.headers["Content-Security-Policy"] = (
                        content_security_policy_value
                    )

                if enable_referer_policy:
                    response.headers["Referer-Policy"] = referer_policy_value

                return response

            return app

        return {}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Middleware error: {str(e)}")


# Middleware: Request ID Middleware
# Slug: request_id_middleware
async def request_id_middleware(request: Request) -> Dict[str, Any]:
    """
    Request ID Middleware
    Generated from middleware ID: mid_b57589383cca459983902cd2f5cca4ec
    """
    try:
        from fastapi import FastAPI, Request, Response
        import os
        import uuid
        import json
        from typing import Optional, Dict, Any

        def setup_request_id_middleware(app: FastAPI) -> FastAPI:
            """
            Setup Request ID middleware with configurable ID type and custom profile
            """

            # Get configuration from environment variables
            id_type = os.getenv("REQUEST_ID_TYPE", "uuid").lower()
            custom_profile_json = os.getenv("REQUEST_ID_CUSTOM_PROFILE", "")
            header_name = os.getenv("REQUEST_ID_HEADER_NAME", "X-Request-ID")

            # Parse custom profile if provided
            custom_profile: Optional[Dict[str, Any]] = None
            if custom_profile_json:
                try:
                    custom_profile = json.loads(custom_profile_json)
                except json.JSONDecodeError:
                    custom_profile = None

            # Validate ID type
            valid_id_types = ["uuid", "x-request-id", "custom"]
            if id_type not in valid_id_types:
                id_type = "uuid"

            def generate_request_id(request: Request) -> str:
                """
                Generate or extract request ID based on configured ID type
                """
                if id_type == "x-request-id":
                    # Use existing X-Request-ID header if present, otherwise generate UUID
                    existing_id = request.headers.get(
                        "X-Request-ID"
                    ) or request.headers.get("x-request-id")
                    if existing_id:
                        return existing_id
                    return str(uuid.uuid4())

                elif id_type == "custom" and custom_profile:
                    # Use custom profile to generate ID
                    # Custom profile can specify:
                    # - prefix: string prefix for the ID
                    # - suffix: string suffix for the ID
                    # - format: "uuid" or "hex" or "numeric"
                    # - length: length for hex/numeric formats

                    prefix = custom_profile.get("prefix", "")
                    suffix = custom_profile.get("suffix", "")
                    format_type = custom_profile.get("format", "uuid").lower()
                    length = int(custom_profile.get("length", 16))

                    if format_type == "uuid":
                        generated_id = str(uuid.uuid4())
                    elif format_type == "hex":
                        generated_id = uuid.uuid4().hex[:length]
                    elif format_type == "numeric":
                        # Generate numeric ID from UUID
                        generated_id = str(uuid.uuid4().int)[:length]
                    else:
                        generated_id = str(uuid.uuid4())

                    # Combine prefix, generated ID, and suffix
                    return f"{prefix}{generated_id}{suffix}"

                else:
                    # Default: generate UUID
                    return str(uuid.uuid4())

            @app.middleware("http")
            async def request_id_middleware(request: Request, call_next):
                # Generate or extract request ID
                request_id = generate_request_id(request)

                # Store request ID in request state for use in other middleware/handlers
                request.state.request_id = request_id

                # Process request
                response = await call_next(request)

                # Add request ID to response headers
                response.headers[header_name] = request_id

                return response

            return app

        return {}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Middleware error: {str(e)}")


# Middleware: Rate Limiter Middleware
# Slug: rate_limiter_middleware
async def rate_limiter_middleware(request: Request) -> Dict[str, Any]:
    """
    Rate Limiter Middleware
    Generated from middleware ID: mid_d9b8fe06c60647b0b5da8a5b2b241265
    """
    try:
        from fastapi import FastAPI, Request, Response, HTTPException
        import os
        import time
        import asyncio
        from typing import Dict, Tuple
        from collections import defaultdict

        def setup_rate_limiter_middleware(app: FastAPI) -> FastAPI:
            """
            Setup Rate Limiter middleware with configurable capacity, refill rate, and exempted paths
            Uses token bucket algorithm for rate limiting
            """

            # Get configuration from environment variables
            capacity = int(
                os.getenv("RATE_LIMITER_CAPACITY", "2000")
            )  # Maximum requests per minute
            refill_rate = int(
                os.getenv("RATE_LIMITER_REFILL_RATE", "600")
            )  # Tokens added per minute
            exempted_path = os.getenv("RATE_LIMITER_EXEMPTED_PATH", "")

            # Validate configuration
            if capacity <= 0:
                capacity = 2000
            if refill_rate <= 0:
                refill_rate = 600
            if refill_rate > capacity:
                refill_rate = capacity  # Refill rate cannot exceed capacity

            # Token bucket storage: {client_id: (tokens, last_refill_time)}
            token_buckets: Dict[str, Tuple[float, float]] = defaultdict(
                lambda: (float(capacity), time.time())
            )

            # Lock for thread-safe access to token buckets
            bucket_lock = asyncio.Lock()

            def get_client_id(request: Request) -> str:
                """
                Get client identifier (IP address) for rate limiting
                """
                # Try to get real IP from various headers (for proxied requests)
                forwarded_for = request.headers.get("X-Forwarded-For")
                if forwarded_for:
                    # X-Forwarded-For can contain multiple IPs, take the first one
                    client_ip = forwarded_for.split(",")[0].strip()
                else:
                    real_ip = request.headers.get("X-Real-IP")
                    if real_ip:
                        client_ip = real_ip
                    else:
                        client_ip = request.client.host if request.client else "unknown"

                return client_ip

            def is_path_exempted(path: str, exempted_path: str) -> bool:
                """
                Check if the request path is exempted from rate limiting
                """
                if not exempted_path:
                    return False

                # Exact match or prefix match
                return path == exempted_path or path.startswith(
                    exempted_path.rstrip("/") + "/"
                )

            def refill_tokens(client_id: str) -> Tuple[float, float]:
                """
                Refill tokens for a client based on elapsed time
                Returns (current_tokens, last_refill_time)
                Note: This should be called within the bucket_lock context
                """
                current_time = time.time()
                tokens, last_refill = token_buckets[client_id]

                # Calculate time elapsed since last refill (in minutes)
                elapsed_minutes = (current_time - last_refill) / 60.0

                # Calculate tokens to add
                tokens_to_add = elapsed_minutes * refill_rate

                # Refill tokens (but don't exceed capacity)
                new_tokens = min(capacity, tokens + tokens_to_add)

                # Update last refill time
                new_last_refill = current_time

                # Update bucket
                token_buckets[client_id] = (new_tokens, new_last_refill)

                return (new_tokens, new_last_refill)

            async def consume_token(client_id: str) -> bool:
                """
                Try to consume a token from the client's bucket
                Returns True if token was consumed, False if rate limit exceeded
                """
                async with bucket_lock:
                    tokens, last_refill = refill_tokens(client_id)

                    if tokens >= 1.0:
                        # Consume one token
                        token_buckets[client_id] = (tokens - 1.0, last_refill)
                        return True
                    else:
                        # Rate limit exceeded
                        return False

            @app.middleware("http")
            async def rate_limiter_middleware(request: Request, call_next):
                # Get request path
                path = request.url.path

                # Check if path is exempted
                if is_path_exempted(path, exempted_path):
                    # Process request without rate limiting
                    response = await call_next(request)
                    return response

                # Get client identifier
                client_id = get_client_id(request)

                # Try to consume a token
                allowed = await consume_token(client_id)

                if not allowed:
                    # Rate limit exceeded
                    raise HTTPException(
                        status_code=429,
                        detail="Rate limit exceeded. Too many requests.",
                        headers={
                            "Retry-After": "60",  # Suggest retrying after 60 seconds
                            "X-RateLimit-Limit": str(capacity),
                            "X-RateLimit-Remaining": "0",
                        },
                    )

                # Process request
                response = await call_next(request)

                # Add rate limit headers to response
                async with bucket_lock:
                    tokens, _ = refill_tokens(client_id)
                    remaining = max(0, int(tokens))
                    response.headers["X-RateLimit-Limit"] = str(capacity)
                    response.headers["X-RateLimit-Remaining"] = str(remaining)

                return response

            return app

        return {}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Middleware error: {str(e)}")


# Middleware Group Dependency Functions


async def default_dependency(request: Request) -> Dict[str, Any]:
    """
    Dependency function for middleware group: default
    Executes all middlewares in the group in sequence
    """
    result = {}

    # Execute request_logger_middleware
    middleware_result = await request_logger_middleware(request)
    if isinstance(middleware_result, dict):
        result.update(middleware_result)
        # Store middleware variables in request.state for API handlers to access
        for key, value in middleware_result.items():
            setattr(request.state, key, value)

    # Execute security_headers_middleware
    middleware_result = await security_headers_middleware(request)
    if isinstance(middleware_result, dict):
        result.update(middleware_result)
        # Store middleware variables in request.state for API handlers to access
        for key, value in middleware_result.items():
            setattr(request.state, key, value)

    # Execute request_id_middleware
    middleware_result = await request_id_middleware(request)
    if isinstance(middleware_result, dict):
        result.update(middleware_result)
        # Store middleware variables in request.state for API handlers to access
        for key, value in middleware_result.items():
            setattr(request.state, key, value)

    # Execute rate_limiter_middleware
    middleware_result = await rate_limiter_middleware(request)
    if isinstance(middleware_result, dict):
        result.update(middleware_result)
        # Store middleware variables in request.state for API handlers to access
        for key, value in middleware_result.items():
            setattr(request.state, key, value)

    # Execute cors_middleware
    middleware_result = await cors_middleware(request)
    if isinstance(middleware_result, dict):
        result.update(middleware_result)
        # Store middleware variables in request.state for API handlers to access
        for key, value in middleware_result.items():
            setattr(request.state, key, value)

    return result
