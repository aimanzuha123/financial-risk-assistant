"""
API Middleware
Handles performance timing, logging, and security headers.
"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from database.connection import SessionLocal
from database.models import AuditLog

class AuditMiddleware(BaseHTTPMiddleware):
    """Logs API requests to console and logs warnings/errors to DB Audit Log."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        # Log errors or warning routes to database audit logs
        if response.status_code >= 400 and "/api/" in request.url.path:
            db = SessionLocal()
            try:
                log = AuditLog(
                    action=f"API Error Response: {request.method} {request.url.path}",
                    category="security",
                    details={
                        "status_code": response.status_code,
                        "method": request.method,
                        "path": request.url.path,
                        "process_time_ms": round(process_time * 1000, 2)
                    },
                    severity="warning" if response.status_code < 500 else "critical"
                )
                db.add(log)
                db.commit()
            except Exception:
                pass
            finally:
                db.close()

        return response
