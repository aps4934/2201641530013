from loguru import logger as _logger
from time import time
from typing import Callable
from flask import g, request

# Configure loguru (file sink, rotation, retention). Adjust path/levels as needed.
_logger.remove()
_logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="10 days",
    level="DEBUG",
    enqueue=True,
    backtrace=True,
    diagnose=True,
)

# Expose a simple logger object for the rest of the app to import
logger = _logger

def init_logging(app) -> None:
    """
    Register Flask request/response logging middleware on the given Flask app.
    Must be called once during app initialization (before serving requests).
    """

    @app.before_request
    def _before_request():
        g._start_time = time()
        # Log incoming request metadata (no console or builtin logging)
        logger.debug("HTTP request start: method={} path={} remote={} ua={} referrer={}",
                     request.method, request.path, request.remote_addr, request.user_agent.string, request.referrer)

    @app.after_request
    def _after_request(response):
        duration = (time() - getattr(g, "_start_time", time())) * 1000.0
        logger.info("HTTP request complete: method={} path={} status={} duration_ms={:.2f} content_length={}",
                    request.method, request.path, response.status_code, duration, request.content_length)
        return response

    @app.teardown_request
    def _teardown_request(exc):
        if exc:
            logger.exception("Unhandled exception during request: {}", exc)