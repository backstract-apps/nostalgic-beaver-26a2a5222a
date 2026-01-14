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
            existing_id = request.headers.get("X-Request-ID") or request.headers.get(
                "x-request-id"
            )
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
        request.state.request_id_middleware = request_id

        # Process request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers[header_name] = request_id

        return response

    return app
