# utils/logger.py
import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs/add_device_logs"
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name, console_level=logging.INFO, file_level=logging.DEBUG):
    """
    返回带时间戳的 logger 实例，仅输出到文件（控制台输出由 pytest 的 log_cli 负责）
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # 避免重复添加 handler

    logger.setLevel(logging.DEBUG)

    # 文件 handler（按大小滚动）
    time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_DIR, f"add_device_{time_str}.log")
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    file_handler.setLevel(file_level)
    file_format = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S")
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    return logger