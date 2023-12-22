import time
rq = time.strftime('%Y-%m-%d', time.localtime(time.time()))

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s - %(levelname)s - %(message)s",
            "use_colors": None
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(asctime)s - %(levelname)s - %(message)s - "%(request_line)s" %(status_code)s'
        }
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"../logs/{rq}_info.log",
            'maxBytes': 1024 * 1024 * 50,  # 日誌大小 50M
            'backupCount': 0,  # 最多備份幾個
        },
        "access": {
            "formatter": "access",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"../logs/{rq}_info.log",
            'maxBytes': 1024 * 1024 * 50,  # 日誌大小 50M
            'backupCount': 0,  # 最多備份幾個
        },
        "error": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"../logs/{rq}_err.log",
            "formatter": "default",
            'maxBytes': 1024 * 1024 * 50,  # 日誌大小 50M
            'backupCount': 0,  # 最多備份幾個
        },
    },
    "loggers": {
        "": {"handlers": ["default", "error"], "level": "INFO"},
        #INFO的話執行才會寫入info
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
}