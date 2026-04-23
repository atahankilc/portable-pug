import logging.config
from typing import Iterable

_FRAMEWORK_LOGGERS = (
    "uvicorn",
    "uvicorn.error",
    "uvicorn.access",
    "gunicorn.error",
    "gunicorn.access",
    "django",
    "django.request",
    "django.server",
    "celery",
)


def configure_logging(
    level: str = "INFO",
    extra_loggers: Iterable[str] = (),
) -> None:
    loggers = {
        "": {"handlers": ["default"], "level": level, "propagate": False},
    }
    for name in (*_FRAMEWORK_LOGGERS, *extra_loggers):
        loggers[name] = {"handlers": ["default"], "level": level, "propagate": False}

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {"()": "shared.logging.formatter.JsonFormatter"},
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "json",
                },
            },
            "loggers": loggers,
        }
    )
