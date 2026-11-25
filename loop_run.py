import os
import sys
import time
import shutil
import subprocess
import config


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TESTS_DIR = os.path.join(BASE_DIR, "tests")
os.chdir(BASE_DIR)

ROUNDS = config.SMOKE_ROUNDS
INTERVAL = config.SMOKE_ROUND_INTERVAL
FORMAT_INTERVAL = 5
ALLURE_DIR = os.path.join(BASE_DIR, "reports", "allure-results")
PYTEST_LOG = os.path.join(BASE_DIR, "logs", "pytest_run.log")


# 每轮测试顺序
TEST_FILES_BEFORE_FORMAT = [
    "test_add_device.py",
    "test_performance_matrix.py",
    "test_detection_recording.py",
    "test_sdcard_retrieval.py"
]

TEST_FILES_AFTER_FORMAT = [
    "test_device_info.py",
    "test_reboot.py",
    "test_delete.py"
]


for i in range(1, ROUNDS + 1):
    print(f"\n{'=' * 60}")
    print(f"  冒烟测试第 {i} / {ROUNDS} 轮")
    print(f"{'=' * 60}")

    os.environ["CURRENT_ROUND"] = str(i)

    if os.path.exists(ALLURE_DIR):
        shutil.rmtree(ALLURE_DIR)
    os.makedirs(ALLURE_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(PYTEST_LOG), exist_ok=True)

    test_files = list(TEST_FILES_BEFORE_FORMAT)

    if i % FORMAT_INTERVAL == 0:
        test_files.append("test_sdcard_format.py")
        print(f"[Run] 第 {i} 轮执行 SD 卡格式化")

    test_files.extend(TEST_FILES_AFTER_FORMAT)

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        *test_files,
        "-m",
        "smoke",
        "-v",
        f"--alluredir={ALLURE_DIR}",
        f"--log-file={PYTEST_LOG}"
    ]

    result = subprocess.run(
        cmd,
        cwd=TESTS_DIR,
        env=os.environ.copy()
    )

    if result.returncode != 0:
        print(f"\n⚠️ 第 {i} 轮存在失败用例，继续下一轮")

    if i < ROUNDS:
        print(f"\n⏳ 第 {i} 轮完成，等待 {INTERVAL} 秒")
        time.sleep(INTERVAL)


os.environ.pop("CURRENT_ROUND", None)

print("\n" + "=" * 60)
print(f"  全部 {ROUNDS} 轮测试完成")
print("=" * 60)