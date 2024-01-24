import os
import logging
from logging.handlers import RotatingFileHandler

LOGGER_MB_LIMIT = 50

log_directory = "/scrapper/log"
os.makedirs(log_directory, exist_ok=True)

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

info_handler = RotatingFileHandler(os.path.join(log_directory, "log_info.log"), mode='a',
                                   maxBytes=LOGGER_MB_LIMIT * 1024 * 1024, backupCount=1,
                                   encoding='utf-8', delay=False)
info_handler.setFormatter(formatter)
info_handler.setLevel(logging.INFO)

error_handler = RotatingFileHandler(os.path.join(log_directory, "log_error.log"), mode='a',
                                    maxBytes=LOGGER_MB_LIMIT * 1024 * 1024, backupCount=1,
                                    encoding='utf-8', delay=False)
error_handler.setFormatter(formatter)
error_handler.setLevel(logging.ERROR)

info_logger = logging.getLogger('info_logger')
info_logger.setLevel(logging.INFO)
info_logger.addHandler(info_handler)

error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.ERROR)
error_logger.addHandler(error_handler)
