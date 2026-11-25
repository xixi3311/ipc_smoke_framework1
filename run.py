# run.py
import os
import sys
import time
import shutil
from datetime import datetime


# ==================== 路径处理 ====================
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
    INTERNAL_DIR = sys._MEIPASS
    sys.path.insert(0, BASE_DIR)
    sys.path.insert(1, INTERNAL_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INTERNAL_DIR = BASE_DIR

os.chdir(BASE_DIR)


# ==================== 准备目录 ====================
for dir_name in ["data", "logs", "outputs", "reports"]:
    os.makedirs(os.path.join(BASE_DIR, dir_name), exist_ok=True)


# ==================== TeeLogger ====================
class TeeLogger:
    def __init__(self, filepath, stdout):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.file = open(filepath, "a", encoding="utf-8")
        self.stdout = stdout
        self.buffer = ""
        self._write_header()

    def _write_header(self):
        header = f"\n{'=' * 70}\n"
        header += (
            f" IPC 冒烟测试启动 | "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        header += f" 项目目录: {BASE_DIR}\n"
        header += f"{'=' * 70}\n"
        self.file.write(header)
        self.file.flush()
        self.stdout.write(header)

    def write(self, message):
        self.buffer += message

        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)

            if line.strip() and not (
                line.strip().startswith("[") and "]" in line[:13]
            ):
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                line = f"[{timestamp}] {line}"

            self.stdout.write(line + "\n")
            self.file.write(line + "\n")
            self.file.flush()

    def flush(self):
        if self.buffer:
            if self.buffer.strip() and not (
                self.buffer.strip().startswith("[")
                and "]" in self.buffer[:13]
            ):
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                self.buffer = f"[{timestamp}] {self.buffer}"

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


RUN_LOG = os.path.join(BASE_DIR, "logs", "run_output.log")
sys.stdout = TeeLogger(RUN_LOG, sys.stdout)


# ==================== 读取配置 ====================
import config


rounds = getattr(config, "SMOKE_ROUNDS", 3)
interval = getattr(config, "SMOKE_ROUND_INTERVAL", 10)
format_interval = 5
allure_dir = os.path.join(BASE_DIR, "reports", "allure-results")


# ==================== 清理旧 Allure 结果 ====================
if os.path.exists(allure_dir):
    shutil.rmtree(allure_dir)

os.makedirs(allure_dir, exist_ok=True)


# ==================== 每轮测试顺序 ====================
test_files = [
    "test_add_device.py",
    "test_performance_matrix.py",
    "test_detection_recording.py",
    "test_sdcard_retrieval.py",
    "test_device_info.py",
    "test_reboot.py",
    "test_delete.py"
]

format_test_file = "test_sdcard_format.py"


# ==================== 切换到 tests 目录 ====================
tests_internal = os.path.join(INTERNAL_DIR, "tests")

if not os.path.exists(tests_internal):
    print(f"❌ 错误: 内部 tests 目录不存在: {tests_internal}")
    input("\n按回车键退出...")
    sys.exit(1)

os.chdir(tests_internal)


# ==================== 执行测试 ====================
print("=" * 70)
print("  IPC 自动化冒烟测试")
print(f"  共 {rounds} 轮，每轮间隔 {interval} 秒")
print(f"  SD 卡每 {format_interval} 轮格式化一次")
print(f"  运行日志: {RUN_LOG}")
print("=" * 70)
print(f"\n项目目录: {BASE_DIR}")
print(f"Allure 报告: {allure_dir}\n")


if getattr(sys, "frozen", False):
    import pytest

    pytest_log = os.path.join(BASE_DIR, "logs", "pytest_run.log")
    os.makedirs(os.path.dirname(pytest_log), exist_ok=True)

    def run_tests(selected_test_files):
        args = [
            *selected_test_files,
            "-m", "smoke",
            "-v",
            f"--alluredir={allure_dir}",
            "-p", "allure_pytest",
            f"--log-file={pytest_log}",
            "--log-file-format=[%(asctime)s] %(message)s",
            "--log-file-date-format=%H:%M:%S",
        ]
        return pytest.main(args)

else:
    import subprocess

    def run_tests(selected_test_files):
        cmd = [
            sys.executable, "-m", "pytest",
            *selected_test_files,
            "-m", "smoke",
            "-v",
            f"--alluredir={allure_dir}"
        ]
        result = subprocess.run(cmd, env=os.environ.copy())
        return result.returncode


for i in range(1, rounds + 1):
    print(f"\n{'=' * 50}")
    print(f"  第 {i} / {rounds} 轮开始")
    print(f"{'=' * 50}\n")

    os.environ["CURRENT_ROUND"] = str(i)
    current_test_files = list(test_files)

    if i % format_interval == 0:
        format_index = current_test_files.index("test_device_info.py")
        current_test_files.insert(format_index, format_test_file)
        print(f"[Run] 第 {i} 轮执行 SD 卡格式化")

    result = run_tests(current_test_files)

    if result != 0:
        print(f"\n⚠️ 第 {i} 轮存在失败用例，继续下一轮...")

    if i < rounds:
        print(f"\n===== 第 {i} 轮完成，等待 {interval} 秒 =====\n")
        time.sleep(interval)


# ==================== 执行完成 ====================
print("\n" + "=" * 70)
print(f"  ✅ 全部 {rounds} 轮测试执行完成！")
print(f"  📄 运行日志: {RUN_LOG}")
print(f"  📊 Allure 报告数据: {allure_dir}")
print("=" * 70)

input("\n按回车键退出...")