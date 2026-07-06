"""Configure logging to console and, optionally, to a file."""

from __future__ import annotations

import logging

from .config import LoggingConfig


def setup_logging(cfg: LoggingConfig) -> None:
    level = getattr(logging, cfg.level.upper(), logging.INFO)
    handlers: list[logging.Handler] = [logging.StreamHandler()]

    if cfg.file:
        handlers.append(logging.FileHandler(cfg.file))

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=handlers,
        force=True,
    )
