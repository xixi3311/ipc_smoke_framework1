# utils/logger.py
import os
import sys
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler

def _get_log_dir():
    """根据运行环境返回日志目录"""
    if getattr(sys, 'frozen', False):
        # 打包后：日志写到 IPCAutoTest.exe 同级目录
        base = os.path.dirname(sys.executable)
    else:
        # 开发环境：utils 的上级目录即项目根目录
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "logs", "add_device_logs")

def get_logger(name, console_level=logging.INFO, file_level=logging.DEBUG):
    """
    返回带时间戳的 logger 实例，仅输出到文件（控制台输出由 pytest 的 log_cli 负责）
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # 避免重复添加 handler

    logger.setLevel(logging.DEBUG)

    # 运行时动态计算路径，并确保目录存在
    log_dir = _get_log_dir()
    os.makedirs(log_dir, exist_ok=True)

    time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"add_device_{time_str}.log")
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    file_handler.setLevel(file_level)
    file_format = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S")
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    return logger