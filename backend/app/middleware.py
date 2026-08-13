import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.logger import get_logger

logger = get_logger("http")

# Paths that are noise — skip verbose logging
_SILENT_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every HTTP request as a single structured JSON line:

      {"ts":"...","level":"INFO","logger":"http","msg":"POST /auth/login 200",
       "request_id":"a1b2c3d4","method":"POST","path":"/auth/login",
       "status":200,"duration_ms":12.4}

    Rules:
      2xx / 3xx  → INFO
      4xx        → WARNING  (client error, not our fault but worth tracking)
      5xx        → ERROR    (our fault)
      unhandled  → ERROR with full traceback
    """

    async def dispatch(self, request: Request, call_next):
        if request.url.path in _SILENT_PATHS:
            return await call_next(request)

        request_id = uuid.uuid4().hex[:8]
        start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.error(
                f"UNHANDLED {request.method} {request.url.path}",
                exc_info=True,
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                },
            )
            raise

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        status = response.status_code

        log_fn = logger.info
        if status >= 500:
            log_fn = logger.error
        elif status >= 400:
            log_fn = logger.warning

        log_fn(
            f"{request.method} {request.url.path} {status}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": status,
                "duration_ms": duration_ms,
            },
        )

        # Echo the request_id back so the client can reference it in bug reports
        response.headers["X-Request-ID"] = request_id
        return response
