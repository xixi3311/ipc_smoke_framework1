# run.py
import os
import sys
import subprocess
import time
import json

# 获取当前 exe 所在目录（打包后也能正常工作）
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

os.chdir(BASE_DIR)

# 导入 config（从 exe 外部读取，用户可修改）
sys.path.insert(0, BASE_DIR)
import config


def main():
    rounds = getattr(config, 'SMOKE_ROUNDS', 3)
    interval = getattr(config, 'SMOKE_ROUND_INTERVAL', 10)
    test_files = [
        "test_add_device.py",
        "test_performance_matrix.py",
        "test_sdcard_retrieval.py",
        "test_device_info.py",
        "test_reboot.py",
        "test_delete.py"
    ]

    print(f"============================================================")
    print(f"  IPC 自动化冒烟测试 - 共 {rounds} 轮，每轮间隔 {interval} 秒")
    print(f"============================================================\n")

    # 切换到 tests 目录
    tests_dir = os.path.join(BASE_DIR, "tests")
    if not os.path.exists(tests_dir):
        print("错误: tests 目录不存在！")
        input("按回车键退出...")
        sys.exit(1)

    os.chdir(tests_dir)

    for i in range(1, rounds + 1):
        print(f"\n========================================")
        print(f"  第 {i} / {rounds} 轮开始")
        print(f"========================================\n")

        cmd = ["pytest"] + test_files + ["-m", "smoke", "-v", "--alluredir=../reports/allure-results"]
        result = subprocess.run(cmd)

        if result.returncode != 0:
            print(f"\n⚠️ 第 {i} 轮存在失败用例，继续执行下一轮...")

        if i < rounds:
            print(f"\n===== 第 {i} 轮完成，等待 {interval} 秒后开始第 {i+1} 轮 =====")
            time.sleep(interval)

    print(f"\n============================================================")
    print(f"  ✅ 全部 {rounds} 轮冒烟测试执行完成！")
    print(f"============================================================")

    input("\n按回车键退出...")


if __name__ == "__main__":
    main()