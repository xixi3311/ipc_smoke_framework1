import os
import sys
import time
import shutil
import importlib.util
import atexit


# ----------------- 运行目录 -----------------

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
    INTERNAL_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INTERNAL_DIR = os.path.abspath(
        os.path.join(BASE_DIR, "..", "..")
    )

sys.path.insert(0, BASE_DIR)
sys.path.insert(1, INTERNAL_DIR)
os.chdir(BASE_DIR)


# ----------------- 加载配置 -----------------

import config
from utils.serial_monitor import SerialMonitor


def load_binding_config():
    config_path = os.path.join(
        BASE_DIR,
        "binding_stress_config.py"
    )

    if not os.path.exists(config_path):
        config_path = os.path.join(
            INTERNAL_DIR,
            "binding_stress_config.py"
        )

    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"找不到绑定压测配置: {config_path}"
        )

    spec = importlib.util.spec_from_file_location(
        "binding_stress_config",
        config_path
    )
    binding_config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(binding_config)
    return binding_config


binding_config = load_binding_config()

for name in (
        "DEVICE_NAME",
        "DEVICE_SN",
        "BINDING_TYPE",
        "DEVICE_TYPE",
        "WIFI_SSID",
        "WIFI_PASSWORD",
        "ADB_DEVICE_SERIAL",
        "PREVIEW_TIMEOUT"
):
    setattr(config, name, getattr(binding_config, name))

RUN_ID = time.strftime("%Y%m%d_%H%M%S")
config.PROJECT_ROOT = BASE_DIR
config.OUTPUT_RESULTS_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "binding_stress"
)
config.RESULT_EXCEL_NAME = (
    f"test_report_{config.DEVICE_NAME}_{RUN_ID}.xlsx"
)
config.SCREENSHOT_DIR = os.path.join(
    BASE_DIR,
    "logs",
    "binding_stress",
    "screenshots"
)
config.SerialConfig.PORT = binding_config.SERIAL_PORT
config.SerialConfig.BAUDRATE = binding_config.SERIAL_BAUDRATE
config.SerialConfig.TIMEOUT = binding_config.SERIAL_TIMEOUT
config.SerialConfig.LOG_DIR = os.path.join(
    BASE_DIR,
    "logs",
    "binding_stress",
    "serial"
)


# ----------------- 初始化输出目录 -----------------

RUN_LOG_DIR = os.path.join(
    BASE_DIR,
    "logs",
    "binding_stress"
)
RUN_LOG = os.path.join(
    RUN_LOG_DIR,
    f"binding_stress_run_{RUN_ID}.log"
)
PYTEST_LOG = os.path.join(
    RUN_LOG_DIR,
    f"binding_stress_pytest_{RUN_ID}.log"
)
ALLURE_DIR = os.path.join(
    BASE_DIR,
    "reports",
    "binding_stress",
    RUN_ID,
    "allure-results"
)
for path in (
        RUN_LOG_DIR,
        config.OUTPUT_RESULTS_DIR,
        config.SCREENSHOT_DIR,
        config.SerialConfig.LOG_DIR,
        ALLURE_DIR
):
    os.makedirs(path, exist_ok=True)

# ---------------- 整场压测共用一个串口连接 ----------------
serial_monitor = SerialMonitor(
    port=binding_config.SERIAL_PORT,
    baudrate=binding_config.SERIAL_BAUDRATE
)
serial_monitor.start_logging()
config.BINDING_STRESS_SERIAL_MONITOR = serial_monitor
atexit.register(serial_monitor.stop_logging)

# ----------------- 运行日志同步到文件 -----------------

class BindingStressLogger:
    def __init__(self, filepath, stdout):
        self.file = open(filepath, "a", encoding="utf-8")
        self.stdout = stdout
        self.buffer = ""

    def write(self, message):
        self.buffer += message

        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            self.stdout.write(line + "\n")
            self.file.write(line + "\n")
            self.file.flush()

    def flush(self):
        if self.buffer:
            self.stdout.write(self.buffer)
            self.file.write(self.buffer)
            self.buffer = ""

        self.stdout.flush()
        self.file.flush()

    def isatty(self):
        return getattr(self.stdout, "isatty", lambda: False)()

    @property
    def encoding(self):
        return getattr(self.stdout, "encoding", "utf-8")


sys.stdout = BindingStressLogger(RUN_LOG, sys.stdout)
sys.stderr = sys.stdout


# ----------------- 执行绑定压测 -----------------

import pytest


tests_dir = os.path.join(INTERNAL_DIR, "tests")
test_file = os.path.join(
    tests_dir,
    "STREEALON",
    "test_binding_stress.py"
)

if not os.path.isfile(test_file):
    raise FileNotFoundError(f"找不到绑定压测用例: {test_file}")

os.chdir(tests_dir)

failed_rounds = []
rounds = binding_config.BINDING_STRESS_ROUNDS
interval = binding_config.BINDING_STRESS_INTERVAL

print("=" * 68)
print(f"蓝牙绑定压测启动: {config.DEVICE_NAME} / {config.DEVICE_SN}")
print(f"绑定入口: {config.BINDING_TYPE}")
print(f"设备类型: {config.DEVICE_TYPE}")
print(f"总轮数: {rounds}，轮间隔: {interval} 秒")
print(f"运行目录: {BASE_DIR}")
print("=" * 68)

for round_num in range(1, rounds + 1):
    print(f"\n{'=' * 60}")
    print(f"绑定压测第 {round_num} / {rounds} 轮")
    print(f"{'=' * 60}")

    os.environ["CURRENT_ROUND"] = str(round_num)

    result = pytest.main([
        os.path.join("STREEALON", "test_binding_stress.py"),
        "-m", "smoke",
        "-v",
        f"--alluredir={ALLURE_DIR}",
        "-p", "allure_pytest",
        f"--log-file={PYTEST_LOG}",
        "--log-file-format=[%(asctime)s] %(message)s",
        "--log-file-date-format=%H:%M:%S"
    ])

    if result != pytest.ExitCode.OK:
        failed_rounds.append(round_num)
        print(f"[BindingStress] 第 {round_num} 轮失败，继续下一轮")
    else:
        print(f"[BindingStress] 第 {round_num} 轮通过")

    if round_num < rounds:
        print(f"[BindingStress] 等待 {interval} 秒")
        time.sleep(interval)

os.environ.pop("CURRENT_ROUND", None)

print("\n" + "=" * 68)
print(f"绑定压测结束，共 {rounds} 轮")
print(f"失败轮次: {failed_rounds if failed_rounds else '无'}")
print(f"Excel: {config.OUTPUT_RESULTS_DIR}")
print(f"运行日志: {RUN_LOG}")
print(f"Pytest 日志: {PYTEST_LOG}")
print(f"串口日志: {config.SerialConfig.LOG_DIR}")
print(f"截图目录: {config.SCREENSHOT_DIR}")
print(f"Allure 数据: {ALLURE_DIR}")
print("=" * 68)

input("\n按回车退出...")