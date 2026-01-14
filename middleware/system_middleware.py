"""
System Middleware Configuration
Generated system-level middleware that applies to the entire application
"""

from fastapi import FastAPI
import os


def setup_system_middleware(app: FastAPI) -> FastAPI:
    """
    Setup system-level middleware (applied once during app startup)
    This function configures all system middleware for the application
    """

    # CORS Middleware

    from middleware.cors_middleware import setup_cors_middleware

    app = setup_cors_middleware(app)

    # Rate Limiter Middleware

    from middleware.rate_limiter_middleware import setup_rate_limiter_middleware

    app = setup_rate_limiter_middleware(app)

    # Request ID Middleware

    from middleware.request_id_middleware import setup_request_id_middleware

    app = setup_request_id_middleware(app)

    # Request Logger Middleware

    from middleware.request_logger_middleware import setup_request_logger_middleware

    app = setup_request_logger_middleware(app)

    # Security Headers Middleware

    from middleware.security_headers_middleware import setup_security_headers_middleware

    app = setup_security_headers_middleware(app)

    return app
