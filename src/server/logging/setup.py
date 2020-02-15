import logging
import sys

from structlog import BoundLogger, configure, dev, get_logger, processors, stdlib

configure(
    processors=[
        stdlib.add_log_level,
        processors.format_exc_info,
        stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=stdlib.LoggerFactory(),
)

formatter = stdlib.ProcessorFormatter(processor=dev.ConsoleRenderer())

handler = logging.StreamHandler()
handler.setFormatter(formatter)

root_logger: logging.Logger = None


def get_root_logger() -> BoundLogger:
    return get_logger("root")


def setup_logging(level: str = "INFO", style: str = "dev", stream: str = "stdout"):
    global root_logger

    if root_logger:
        return

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    set_level(level)
    set_style(style)
    set_stream(stream)


def set_level(level: str = "INFO"):
    root_logger.setLevel(getattr(logging, level, "INFO"))


def set_stream(stream: str = "stdout"):
    handler.setStream(getattr(sys, stream, "stdout"))


def set_style(style):
    if style == "keys":
        formatter.processor = processors.KeyValueRenderer()
    if style == "json":
        formatter.processor = processors.JSONRenderer()
    if style == "dev":
        formatter.processor = dev.ConsoleRenderer()
