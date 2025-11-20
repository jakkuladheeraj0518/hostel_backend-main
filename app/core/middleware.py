"""
Middleware manager
"""
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import setup_logger

logger = setup_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
        )
        return response

