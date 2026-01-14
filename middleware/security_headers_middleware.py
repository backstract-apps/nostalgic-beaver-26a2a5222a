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
        os.getenv("SECURITY_HEADERS_X_CONTENT_TYPE_OPTIONS", "false").lower() == "true"
    )
    enable_content_security_policy = (
        os.getenv("SECURITY_HEADERS_CONTENT_SECURITY_POLICY", "false").lower() == "true"
    )
    enable_referer_policy = (
        os.getenv("SECURITY_HEADERS_REFERER_POLICY", "false").lower() == "true"
    )

    # HTTPS enforcement
    force_https = os.getenv("SECURITY_HEADERS_FORCE_HTTPS", "false").lower() == "true"

    # Trusted host validation
    trusted_host_enabled = (
        os.getenv("SECURITY_HEADERS_TRUSTED_HOST", "false").lower() == "true"
    )
    trusted_hosts = os.getenv("SECURITY_HEADERS_TRUSTED_HOST_LIST", "").split(",")
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
                return Response(status_code=301, headers={"Location": https_url})

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
            response.headers["X-Content-Type-Options"] = x_content_type_options_value

        if enable_content_security_policy:
            response.headers["Content-Security-Policy"] = content_security_policy_value

        if enable_referer_policy:
            response.headers["Referer-Policy"] = referer_policy_value

        return response

    return app
