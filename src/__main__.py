#!/usr/bin/env python3

from asyncio import set_event_loop_policy
from os import environ

from aiohttp.web import run_app
from prometheus_client.core import REGISTRY
from structlog import get_logger
from uvloop import EventLoopPolicy

from server import Server
from server.logging import AccessLogger, LoggingContext, get_root_logger, setup_logging

if __name__ == "__main__":
    setup_logging(
        level=environ.get("LOG_LEVEL", "DEBUG"), style=environ.get("LOG_STYLE", "dev")
    )
    root_logger = get_root_logger()
    set_event_loop_policy(EventLoopPolicy())
    try:
        server = Server()
        REGISTRY.register(server.store)
        REGISTRY.register(server.stats_collector)
        REGISTRY.register(server.task_collector)
        run_app(
            server,
            host="0.0.0.0",
            port=5000,
            access_log=get_logger("aiohttp.web"),
            access_log_class=AccessLogger,
        )
    except Exception:
        trace = LoggingContext()
        trace.capture_error()
        root_logger.error("Error running Server", **trace.for_logging())
