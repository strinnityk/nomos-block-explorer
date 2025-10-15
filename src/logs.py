import os
from logging.config import dictConfig


def get_logging_config(nbe_log_level: str, sqla_log_level: str):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "[%(asctime)s] [%(levelname)s] [%(name)s] (%(module)s:%(lineno)d): %(message)s",
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
            "level": nbe_log_level,
        },
        "loggers": {
            # ---- SQLAlchemy / SQLModel ----
            "sqlalchemy": {"level": sqla_log_level, "handlers": [], "propagate": False},
            "sqlalchemy.engine": {"level": sqla_log_level, "handlers": [], "propagate": False},
            "sqlalchemy.pool": {"level": sqla_log_level, "handlers": [], "propagate": False},
            "sqlalchemy.orm": {"level": sqla_log_level, "handlers": [], "propagate": False},
            "sqlalchemy.dialects": {"level": sqla_log_level, "handlers": [], "propagate": False},
            # ---- Httpx / HttpCore / Urllib3 ----
            "httpx": {"level": "WARNING", "handlers": ["console"], "propagate": False},
            "httpcore": {"level": "WARNING", "handlers": ["console"], "propagate": False},
            "urllib3": {"level": "WARNING", "handlers": ["console"], "propagate": False},
            # ---- Uvicorn / FastAPI ----
            "uvicorn": {"level": "INFO", "handlers": ["uvicorn"], "propagate": False},
            # "uvicorn.error":  {"level": "INFO", "handlers": ["uvicorn"], "propagate": False},
            "uvicorn.access": {"level": "WARNING", "handlers": ["uvicorn_access"], "propagate": False},
            # ---- Application ----
            "src": {"level": nbe_log_level, "handlers": ["console"], "propagate": False},
        },
    }


def setup_logging():
    nbe_log_level = os.getenv("NBE_LOG_LEVEL", "INFO").upper()
    sqla_log_level = os.getenv("SQLALCHEMY_LOG_LEVEL", "ERROR").upper()
    logging_config = get_logging_config(nbe_log_level, sqla_log_level)
    dictConfig(logging_config)
