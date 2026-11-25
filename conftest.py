# conftest.py（原始版本，放在 exe 外部）
# 全局 fixture、页面初始化、测试结果监听和失败截图处理
import os
import sys
from datetime import datetime
import pytest
import uiautomator2 as u2
import allure
import allure_pytest
import config
import atexit

# 导入所有 Page 类
from pages.first_page.home_page import HomePage
from pages.second_page.live_page import LivePage
from pages.third_page.cloud_replay_page import CloudReplayPage
from pages.third_page.sdcard_replay_page import SdCardReplayPage
from pages.third_page.setting_page import SettingsPage
from utils.serial_monitor import SerialMonitor
from utils.result_exporter import PerformanceResultExporter


# ============ 强制锁定工作目录到项目根目录 ============
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)
# =====================================================


@pytest.fixture(scope="session", autouse=True)
def serial_logger():
    """绑定压测期间复用 runner 管理的串口，其余场景保持原行为"""
    monitor = getattr(
        config,
        "BINDING_STRESS_SERIAL_MONITOR",
        None
    )

    if monitor:
        yield monitor
        return

    monitor = SerialMonitor()
    monitor.start_logging()

    yield monitor

    monitor.stop_logging()

    if monitor.current_log_path and os.path.exists(monitor.current_log_path):
        try:
            log_filename = os.path.basename(monitor.current_log_path)
            allure.attach.file(
                monitor.current_log_path,
                name=f"设备串口日志 ({log_filename})",
                attachment_type=allure.attachment_type.TEXT
            )
        except Exception as e:
            print(f"[conftest] 串口日志附加到 Allure 失败: {e}")


@pytest.fixture(scope="session")
def driver():
    """提供 uiautomator2 连接对象的 Session 级 fixture"""
    device_serial = config.ADB_DEVICE_SERIAL
    print(f"\n[Fixture] 正在连接测试设备: {device_serial if device_serial else '默认USB设备'}")

    d = u2.connect(device_serial)
    yield d


@pytest.fixture(autouse=True)
def init_pages(request, driver):
    """自动为每个测试类注入 driver 和所有 Page 对象实例"""

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
    Pytest 钩子：监听用例执行状态。
    记录 PASS、FAIL 和 SKIP；失败时生成截图；
    同时把测试用例提供的说明写入 Excel 备注。
    """
    outcome = yield
    report = outcome.get_result()

    # 所有普通用例统一记录结果，性能压测用例由自身记录
    if report.when == "call" and "test_performance_matrix" not in item.nodeid:
        # run.py / loop_run.py 每轮启动前写入当前轮次
        round_num = int(os.environ.get("CURRENT_ROUND", "1"))

        # 识别测试类型
        nodeid = item.nodeid
        if "test_binding_stress" in nodeid:
            test_type = "绑定压测"
        elif "test_add_device" in nodeid:
            test_type = "设备绑定"
        elif "test_delete" in nodeid:
            test_type = "设备删除"
        elif "test_reboot" in nodeid:
            test_type = "设备重启"
        elif "test_device_info" in nodeid:
            test_type = "信息校验"
        elif "test_sdcard_retrieval" in nodeid:
            test_type = "卡回看检索"
        elif "test_live_and_replay" in nodeid:
            test_type = "Live/回看"
        else:
            test_type = "其他"

        # pytest 的跳过状态单独记录，不能按失败处理
        if report.outcome == "passed":
            status = "PASS"
        elif report.outcome == "skipped":
            status = "SKIP"
        else:
            status = "FAIL"

        remark = ""

        # 失败原因或跳过原因先写入备注
        if status in ("FAIL", "SKIP") and report.longrepr:
            remark = str(report.longrepr)[:500]

        # 测试方法可通过 self.result_remark 提供业务说明
        instance_remark = getattr(
            item.instance,
            "result_remark",
            ""
        )

        if instance_remark:
            if remark:
                remark = f"{remark}；{instance_remark}"
            else:
                remark = instance_remark

        exporter = PerformanceResultExporter()
        exporter.record_result(
            round_num=round_num,
            test_type=test_type,
            mode="-",
            biz_type=item.name,
            duration=getattr(report, "duration", 0),
            status=status,
            remark=remark
        )

        # 只有真正失败的用例才写入错误详情
        if status == "FAIL":
            exporter.record_error(
                round_num=round_num,
                test_type=test_type,
                test_case=item.name,
                error_msg=remark
            )

    # setup 或用例执行阶段失败时截图；跳过的用例不截图
    if report.failed and report.when in ("setup", "call"):
        driver_obj = None
        test_instance = getattr(item, "instance", None)

        if test_instance:
            if hasattr(test_instance, "driver"):
                driver_obj = test_instance.driver
            elif (
                hasattr(test_instance, "home_page")
                and hasattr(test_instance.home_page, "driver")
            ):
                driver_obj = test_instance.home_page.driver

        # setup 阶段失败时，测试类实例可能还没有 driver
        if not driver_obj:
            funcargs = getattr(item, "funcargs", {})
            driver_obj = funcargs.get("driver")

        if not driver_obj:
            print(
                f"\n[conftest] {report.when} 阶段失败，"
                "当前没有可用 driver，无法生成截图"
            )
            return

        try:
            now_str = datetime.now().strftime(
                "%Y%m%d_%H%M%S_%f"
            )[:-3]
            date_folder = datetime.now().strftime("%Y%m%d")

            # 使用运行配置中的截图目录，避免打包时写入 _MEI 临时目录
            screenshot_root = getattr(
                config,
                "SCREENSHOT_DIR",
                os.path.join(
                    config.PROJECT_ROOT,
                    "logs",
                    "screenshots"
                )
            )
            save_dir = os.path.join(
                screenshot_root,
                date_folder
            )
            os.makedirs(save_dir, exist_ok=True)

            clean_item_name = (
                item.name
                .replace("[", "_")
                .replace("]", "_")
            )
            file_name = f"fail_{clean_item_name}_{now_str}.png"
            img_path = os.path.join(save_dir, file_name)

            driver_obj.screenshot(img_path)

            display_time = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            )[:-3]

            allure.attach.file(
                img_path,
                name=(
                    f"失败现场截图 [{clean_item_name}] "
                    f"- 时间: {display_time}"
                ),
                attachment_type=allure.attachment_type.PNG
            )

            print(f"\n[conftest] 失败截图已生成: {img_path}")
            print(f"[conftest] 报错精确时间点: {display_time}")

        except Exception as e:
            print(f"\n[conftest] 截图保存或挂载失败: {e}")








