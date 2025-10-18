import colorlog
import datetime
import logging
import os
from pathlib import Path

_filename = 'autopilot.log'

# Rename existing log file to create new one.
if os.path.exists(_filename):
    filename_only = Path(_filename).stem
    t = os.path.getmtime(_filename)
    v = datetime.datetime.fromtimestamp(t)
    x = v.strftime('%Y-%m-%d %H-%M-%S')
    os.rename(_filename, f"{filename_only} {x}.log")

# Define the logging config.
logging.basicConfig(
    filename=_filename,
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d [%(name)s] %(levelname)-8s %(message)s',
    datefmt='%H:%M:%S'
)


def get_module_logger(name):
    import colorlog as _colorlog
    import logging as _logging

    logger = _colorlog.getLogger(name)
    handler = _colorlog.StreamHandler()
    formatter = _colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s.%(msecs)03d [%(name)s] %(levelname)-8s%(reset)s %(message)s",
        datefmt="%H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red'
        }
    )
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
    logger.setLevel(_logging.INFO)
    return logger


def set_global_log_level(level):
    import logging as _logging

    _logging.getLogger().setLevel(level)
    for name, logger in _logging.Logger.manager.loggerDict.items():
        if isinstance(logger, _logging.Logger):
            logger.setLevel(level)


def get_logger():
    return get_module_logger("GLOBAL")


logger = get_logger()


