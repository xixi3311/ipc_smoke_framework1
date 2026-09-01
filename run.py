# run.py
import os
import sys
import time
import shutil

# ============================================================
# 路径处理
# ============================================================

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    INTERNAL_DIR = sys._MEIPASS
    # exe 所在目录优先级 > 打包内部目录
    sys.path.insert(0, BASE_DIR)
    sys.path.insert(1, INTERNAL_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INTERNAL_DIR = BASE_DIR

os.chdir(BASE_DIR)

# ============================================================
# 准备目录
# ============================================================

for dir_name in ["data", "logs", "outputs", "reports"]:
    os.makedirs(os.path.join(BASE_DIR, dir_name), exist_ok=True)

# ============================================================
# 读取配置
# ============================================================

import config

rounds = getattr(config, 'SMOKE_ROUNDS', 3)
interval = getattr(config, 'SMOKE_ROUND_INTERVAL', 10)
allure_dir = os.path.join(BASE_DIR, "reports", "allure-results")

# ============================================================
# 清理旧 allure 结果
# ============================================================

if os.path.exists(allure_dir):
    shutil.rmtree(allure_dir)
os.makedirs(allure_dir, exist_ok=True)

# ============================================================
# 测试文件列表
# ============================================================

test_files = [
    "test_add_device.py",
    "test_performance_matrix.py",
    "test_sdcard_retrieval.py",
    "test_device_info.py",
    "test_reboot.py",
    "test_delete.py"
]

# ============================================================
# 切换到内部 tests 目录
# ============================================================

tests_internal = os.path.join(INTERNAL_DIR, "tests")
if not os.path.exists(tests_internal):
    print(f"错误: 内部 tests 目录不存在！")
    input("\n按回车键退出...")
    sys.exit(1)

os.chdir(tests_internal)

# ============================================================
# 执行测试（多轮）
# ============================================================

print("=" * 60)
print(f"  IPC 自动化冒烟测试")
print(f"  共 {rounds} 轮，每轮间隔 {interval} 秒")
print("=" * 60)
print(f"\n项目目录: {BASE_DIR}")
print(f"Allure 报告: {allure_dir}\n")

if getattr(sys, 'frozen', False):
    import pytest


    # 不要在这里 import allure_pytest！让 pytest -p 自己加载

    def run_tests():
        args = [
            *test_files,
            "-m", "smoke",
            "-v",
            f"--alluredir={allure_dir}",
            "-p", "allure_pytest",
        ]
        return pytest.main(args)
else:
    import subprocess


    def run_tests():
        cmd = [
            sys.executable, "-m", "pytest",
            *test_files,
            "-m", "smoke",
            "-v",
            f"--alluredir={allure_dir}"
        ]
        result = subprocess.run(cmd)
        return result.returncode

for i in range(1, rounds + 1):
    print(f"\n{'=' * 40}")
    print(f"  第 {i} / {rounds} 轮开始")
    print(f"{'=' * 40}\n")

    result = run_tests()

    if result != 0:
        print(f"\n⚠️ 第 {i} 轮存在失败用例，继续执行下一轮...")

    if i < rounds:
        print(f"\n===== 第 {i} 轮完成，等待 {interval} 秒 =====\n")
        time.sleep(interval)

# ============================================================
# 执行完成
# ============================================================

print("\n" + "=" * 60)
print("  ✅ 全部测试执行完成！")
print("=" * 60)
print(f"\nAllure 报告数据已生成: {allure_dir}")

input("\n按回车键退出...")