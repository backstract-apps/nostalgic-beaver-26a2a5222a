from fastapi import FastAPI, Request
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from middleware.system_middleware import setup_system_middleware


from database import engine

from prometheus_client import Counter, Histogram, Gauge, make_asgi_app
import models
import uvicorn
from routes import router

import time
import logging_loki
from multiprocessing import Queue
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor  # Re-add this import
import logging
import sys
import os
from telemetry_config import setup_telemetry_and_logging
from fastapi_mcp import FastApiMCP


from middleware.request_log_storage.migration import run as run_migration
from middleware.request_log_storage.loguru_sink import install_loguru_db_sink

from dotenv import load_dotenv


try:
    load_dotenv()
except Exception as e:
    logger.debug(f"Skipping .env loading: {e}")

setup_telemetry_and_logging()


# Database setup
try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    logger.debug(f"Skipping table creation: {e}")



# Auto-run request_logs migration if DB logging for requests is enabled
_req_log_db_enabled = (os.getenv("REQUEST_LOG_DB_ENABLED", "true") or "true").strip().lower() == "true"
if _req_log_db_enabled:
    try:
        # Safe to run repeatedly due to IF NOT EXISTS in DDL
        run_migration()
    except Exception as e:
        # Do not crash app startup over non-critical log storage table creation
        logger.warning(f"Skipping request_logs migration: {e}")
    
    try:
        install_loguru_db_sink()
    except Exception as e:
        logger.warning(f"Skipping installation of loguru DB sink: {e}")
    

# Prometheus core metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'http_status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency',
                            ['method', 'endpoint', 'http_status'])
IN_PROGRESS = Gauge('http_requests_in_progress', 'HTTP requests in progress')

app = FastAPI(title='Mayson Generated APIs - nostalgic-beaver-26a2a5222a', debug=False,
              docs_url='/docs',
              openapi_url='/openapi.json',
              root_path='/us-west-1-backstractelb-580329-coll-85fd6620c07e48dc8f1e5ab58f9c1e28')


# Apply system middleware (CORS, security headers, etc.)
app = setup_system_middleware(app)


# Fix OpenAPI schema so Swagger UI uses correct base URL
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        routes=app.routes,
    )
    
    # Set correct server URL for Swagger UI "Try it out"
    openapi_schema["servers"] = [{"url": "/us-west-1-backstractelb-580329-coll-85fd6620c07e48dc8f1e5ab58f9c1e28"}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

FastAPIInstrumentor.instrument_app(app)  # Re-add this line






# Global Exception Handlers
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    import traceback
    status_code = getattr(exc, 'status_code', 500) or getattr(exc, 'code', 500)
    
    # Log detailed error information
    logger.error(f"Exception in {request.method} {request.url.path}: {str(exc)}")
    logger.error(f"Exception type: {type(exc).__name__}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Check for specific error types and provide better messages
    error_message = str(exc)
    if "Expecting value: line 1 column 1" in error_message:
        error_message = "Failed to parse platform API response - resource may not exist or endpoint unavailable"
    elif "404" in error_message or "Not Found" in error_message:
        error_message = "Resource not found on platform - check resource configuration and permissions"
    
    return JSONResponse(
        status_code=500,
        content={
            "status": f"{status_code}",
            "message": f"Global exception caught: {error_message}"
        }
    )

@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": f"{exc.status_code}",
            "message": f"{exc.detail}"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    status_code = getattr(exc, 'status_code', 500) or getattr(exc, 'code', 500)
    return JSONResponse(
        status_code=500,
        content={
            "status": f"{status_code}",
            "message": f"{str(exc)}"
        }
    )





app.include_router(
    router,
    prefix='/api',
    tags=['APIs v1']
)


# Middleware for Prometheus metrics
@app.middleware('http')
async def prometheus_middleware(request: Request, call_next):
    method = request.method
    path = request.url.path
    start_time = time.time()
    status_code=None

    IN_PROGRESS.inc()  # Increment in-progress requests

    # Log incoming request details for file uploads
    if "file-upload" in path:
        logger.info(f"Incoming file upload request: {method} {path}")
        logger.info(f"Query params: {dict(request.query_params)}")
        logger.info(f"Headers: {dict(request.headers)}")

    try:
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time()-start_time)*1000
        if "/metrics" not in request.url.path and "/loki" not in request.url.path:
            status_code = response.status_code
            emoji = "➡️"
            if 200 <= status_code < 300:
                emoji += " ✅"  # Success
                log_level = logger.info
            elif 300 <= status_code < 400:
                emoji += " ↪️"  # Redirection
                log_level = logger.info
            elif 400 <= status_code < 500:
                emoji += " ⚠️"  # Client Error
                log_level = logger.warning
            else:  # 500 and above
                emoji += " ❌"  # Server Error
                log_level = logger.error

            # Create a readable response representation
            response_info = {
                "status": status_code,
                "media_type": getattr(response, 'media_type', None),
                "headers": dict(response.headers) if hasattr(response, 'headers') else {}
            }
            
            log_level(
                f"{emoji} {request.method} {request.url.path} Status: {status_code} response:{response_info} ⏱️ Time: {process_time:.2f}ms"
            )
            
            # For errors, try to log response body if available
            if status_code >= 400 and hasattr(response, 'body'):
                try:
                    response_body = getattr(response, 'body', None)
                    if response_body:
                        logger.error(f"Error response body: {response_body[:500]}")
                except:
                    pass
    except Exception as e:
        status_code = 500  # Internal server error
        raise e
    finally:
        duration = time.time() - start_time
        REQUEST_COUNT.labels(method=method, endpoint=path, http_status=status_code).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=path, http_status=status_code).observe(duration)
        IN_PROGRESS.dec()  # Decrement in-progress requests

    return response


# Prometheus' metrics endpoint
prometheus_app = make_asgi_app()
app.mount('/metrics', prometheus_app)

mcp = FastApiMCP(app, name='Mayson Generated APIs - nostalgic-beaver-26a2a5222a', description='Mayson Generated APIs - nostalgic-beaver-26a2a5222a')
mcp.mount()


def main():
    uvicorn.run('main:app', host='127.0.0.1', port=7070, reload=True)


if __name__ == '__main__':
    main()