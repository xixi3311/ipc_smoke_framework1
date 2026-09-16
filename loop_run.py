# loop_run.py
import os
import sys
import time
import shutil
import subprocess

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

# 测试顺序：绑定 → 出图/信息/重启 → 删除
test_files = [
    "test_add_device.py",
    "test_performance_matrix.py",
    "test_reboot.py",
    "test_delete.py"
]

ROUNDS = 30
INTERVAL = 10  # 每轮间隔（秒）
allure_dir = os.path.join(BASE_DIR, "reports", "allure-results")

for i in range(1, ROUNDS + 1):
    print(f"\n{'='*60}")
    print(f"  🔥 压测第 {i} / {ROUNDS} 轮")
    print(f"{'='*60}")

    # 每轮清理旧 allure 结果（避免数据膨胀，也可注释掉保留全部）
    if os.path.exists(allure_dir):
        shutil.rmtree(allure_dir)
    os.makedirs(allure_dir, exist_ok=True)

    # 执行测试
    cmd = [
        sys.executable, "-m", "pytest",
        *test_files,
        "-m", "smoke",
        "-v",
        f"--alluredir={allure_dir}",
        "--log-file=logs/pytest_run.log",
    ]

    result = subprocess.run(cmd, cwd=os.path.join(BASE_DIR, "tests"))

    if result.returncode != 0:
        print(f"\n⚠️ 第 {i} 轮存在失败，继续下一轮...")

    if i < ROUNDS:
        print(f"\n⏳ 第 {i} 轮完成，等待 {INTERVAL} 秒后继续...")
        time.sleep(INTERVAL)

print("\n" + "="*60)
print("  ✅ 全部 30 轮压测完成！")
print("="*60)