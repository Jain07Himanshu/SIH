import json
import logging
import sys
import time
from typing import Any
from contextlib import contextmanager

class StructuredJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra_data"):
            log_obj.update(record.extra_data)
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredJsonFormatter())
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    root_logger.handlers = [handler]

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

class StructuredLogger:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def log(self, level: int, message: str, **kwargs: Any) -> None:
        extra = {"extra_data": kwargs}
        self.logger.log(level, message, extra=extra)

    def info(self, message: str, **kwargs: Any) -> None:
        self.log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self.log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self.log(logging.ERROR, message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        self.log(logging.DEBUG, message, **kwargs)

@contextmanager
def log_operation(logger: StructuredLogger, operation: str, **kwargs: Any):
    start_time = time.perf_counter()
    logger.info(f"Started operation: {operation}", operation=operation, status="started", **kwargs)
    try:
        yield
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(f"Completed operation: {operation}", operation=operation, duration_ms=duration_ms, status="success", **kwargs)
    except Exception as e:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.error(f"Failed operation: {operation} - {str(e)}", operation=operation, duration_ms=duration_ms, status="error", error=str(e), **kwargs)
        raise
