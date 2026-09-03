# conftest.py（原始版本，放在 exe 外部）
import os
import sys
import time
from datetime import datetime
import pytest
import uiautomator2 as u2
import allure
import io
import config
import allure_pytest  #  显式导入 allure-pytest 插件

# 导入所有 Page 类
from pages.first_page.home_page import HomePage
from pages.second_page.live_page import LivePage
from pages.third_page.cloud_replay_page import CloudReplayPage
from pages.third_page.sdcard_replay_page import SdCardReplayPage
from pages.third_page.setting_page import SettingsPage
from utils.serial_monitor import SerialMonitor

# ============  强制锁定工作目录到项目根目录 ============
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)
# =====================================================


@pytest.fixture(scope="session", autouse=True)
def serial_logger():
    """全局自动开启串口日志，整个测试 Session 期间持续抓取"""
    monitor = SerialMonitor()
    monitor.start_logging()

    yield monitor

    monitor.stop_logging()

    if monitor.current_log_path and os.path.exists(monitor.current_log_path):
        try:
            log_filename = os.path.basename(monitor.current_log_path)
            allure.attach.file(
                monitor.current_log_path,
                name=f" 设备串口日志 ({log_filename})",
                attachment_type=allure.attachment_type.TEXT
            )
        except Exception as e:
            print(f"[conftest] ❌ 串口日志附加至 Allure 失败: {e}")


@pytest.fixture(scope="session")
def driver():
    """提供 uiautomator2 连接对象的 Session 级 fixture"""
    device_serial = config.ADB_DEVICE_SERIAL
    print(f"\n[Fixture] 正在连接测试设备: {device_serial if device_serial else '默认USB设备'}")

    d = u2.connect(device_serial)
    yield d


@pytest.fixture(autouse=True)
def init_pages(request, driver):
    """
    自动为每个测试类注入 driver 和所有的 Page 对象实例
    """
    if request.cls:
        request.cls.driver = driver
        request.cls.home_page = HomePage(driver)
        request.cls.live_page = LivePage(driver)
        request.cls.cloud_page = CloudReplayPage(driver)
        request.cls.sdcard_page = SdCardReplayPage(driver)
        request.cls.settings_page = SettingsPage(driver)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Pytest 钩子：监听用例执行状态
    当用例失败时，记录用例名称与时间戳，保存本地并挂载 Allure 附件
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver_obj = None

        if item.instance:
            if hasattr(item.instance, "driver"):
                driver_obj = item.instance.driver
            elif hasattr(item.instance, "home_page") and hasattr(item.instance.home_page, "driver"):
                driver_obj = item.instance.home_page.driver

        if not driver_obj and "driver" in item.funcargs:
            driver_obj = item.funcargs["driver"]

        if driver_obj:
            try:
                now_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                date_folder = datetime.now().strftime("%Y%m%d")

                save_dir = os.path.join("logs", "screenshots", date_folder)
                os.makedirs(save_dir, exist_ok=True)

                clean_item_name = item.name.replace("[", "_").replace("]", "_")

                file_name = f"fail_{clean_item_name}_{now_str}.png"
                img_path = os.path.join(save_dir, file_name)

                driver_obj.screenshot(img_path)

                display_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

                allure.attach.file(
                    img_path,
                    name=f"❌ 失败现场截图 [{clean_item_name}] - 时间: {display_time}",
                    attachment_type=allure.attachment_type.PNG
                )
                print(f"\n[conftest] 🟢 失败截图已生成: {img_path}")
                print(f"[conftest] 🟢 报错精确时间点: {display_time}")

            except Exception as e:
                print(f"\n[conftest] ❌ 截图挂载失败: {e}")








