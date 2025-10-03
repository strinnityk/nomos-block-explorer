import os
from logging.config import dictConfig

_LEVEL = os.getenv("NBE_LOG_LEVEL", "INFO").upper()
_SQLA_LEVEL = os.getenv("SQLALCHEMY_LOG_LEVEL", "ERROR").upper()

_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "uvicorn": {
            "format": "[%(asctime)s] [%(levelname)s] [uvicorn] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "uvicorn_access": {
            "format": '%(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "standard",
        },
        "uvicorn": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "uvicorn",
        },
        "uvicorn_access": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "uvicorn_access",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": _LEVEL,
    },
    "loggers": {
        # ---- SQLAlchemy / SQLModel ----
        "sqlalchemy": {"level": _SQLA_LEVEL, "handlers": [], "propagate": False},
        "sqlalchemy.engine": {"level": _SQLA_LEVEL, "handlers": [], "propagate": False},
        "sqlalchemy.pool": {"level": _SQLA_LEVEL, "handlers": [], "propagate": False},
        "sqlalchemy.orm": {"level": _SQLA_LEVEL, "handlers": [], "propagate": False},
        "sqlalchemy.dialects": {"level": _SQLA_LEVEL, "handlers": [], "propagate": False},
        # ---- Uvicorn / FastAPI ----
        "uvicorn": {"level": "INFO", "handlers": ["uvicorn"], "propagate": False},
        # "uvicorn.error":  {"level": "INFO", "handlers": ["uvicorn"], "propagate": False},
        "uvicorn.access": {"level": "WARNING", "handlers": ["uvicorn_access"], "propagate": False},
        # Your app namespace
        "app": {"level": _LEVEL, "handlers": ["console"], "propagate": False},
    },
}


def setup_logging():
    dictConfig(_LOGGING_CONFIG)
