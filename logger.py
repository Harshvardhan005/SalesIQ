"""
SalesIQ — Structured Logging
Configures application-wide logging with JSON-style output for production
and human-readable format for development.
"""
import logging
import sys
import uuid
from datetime import datetime, timezone

from flask import request, g


def configure_logging(debug: bool = False):
    """Call once at app startup to set up root logger."""
    log_level = logging.DEBUG if debug else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid duplicating handlers on hot-reload
    if not root_logger.handlers:
        root_logger.addHandler(handler)

    # Silence noisy third-party loggers
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return logging.getLogger("salesiq")


def get_logger(name: str = "salesiq"):
    return logging.getLogger(name)


def register_request_logging(app):
    """Register before/after request hooks for request-level logging."""
    logger = get_logger("salesiq.request")

    @app.before_request
    def before_request_log():
        g.request_id = str(uuid.uuid4())[:8]
        g.start_time = datetime.now(timezone.utc)

    @app.after_request
    def after_request_log(response):
        duration_ms = None
        if hasattr(g, "start_time"):
            delta = datetime.now(timezone.utc) - g.start_time
            duration_ms = round(delta.total_seconds() * 1000, 2)

        req_id = getattr(g, "request_id", "?")
        logger.info(
            f"[{req_id}] {request.method} {request.path} → {response.status_code} ({duration_ms}ms)"
        )
        response.headers["X-Request-ID"] = req_id
        return response
