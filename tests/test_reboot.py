# tests/test_reboot.py
import pytest
import allure
import time
import config
from pages.first_page.home_page import HomePage
from pages.second_page.live_page import LivePage
from pages.third_page.setting_page import SettingsPage


@allure.epic("IPC 自动化测试框架")
@allure.feature("设备重启（含日志校验）")
class TestReboot:

    TARGET_DEVICE = getattr(config, "DEVICE_NAME", "摄像机")
    REBOOT_WAIT_TIME = 90
    MAX_RETRY = 3
    RETRY_INTERVAL = 30

    @pytest.fixture(autouse=True)
    def setup_pages(self, driver):
        self.driver = driver
        self.home_page = HomePage(driver)
        self.live_page = LivePage(driver)
        self.settings_page = SettingsPage(driver)
        self.home_page.ensure_back_to_home()

    @allure.story("重启设备并验证出图（含串口日志校验）")
    @pytest.mark.smoke
    def test_reboot_device(self, serial_logger):
        device_name = self.TARGET_DEVICE

        # ========== 1. 进入设置并执行重启 ==========
        with allure.step(f"进入设备 [{device_name}] Live 预览"):
            self.home_page.click_play_button(device_name)
            self.live_page.wait_for_stream_loaded()

        with allure.step("进入设备设置页"):
            self.live_page.click_settings_gear()
            assert self.settings_page.is_on_settings_page(), "未能进入设置页"

        with allure.step("点击『重启设备』并确认弹窗"):
            self.settings_page.click_reboot_device()
            time.sleep(0.5)
            assert self.settings_page.confirm_reboot_dialog(), "确认重启弹窗失败"
            print("[Test] ✅ 重启指令已下发")

        # ========== 2. 串口日志检测 reboot 关键字 ==========
        with allure.step("串口日志检测 reboot 命令"):
            print("[Test] ⏳ 检测串口日志中的 reboot 命令...")
            reboot_detected = serial_logger.search_keyword("reboot", timeout=15)
            if not reboot_detected:
                reboot_detected = serial_logger.search_keyword("Reboot", timeout=5)

            if reboot_detected:
                print("[Test] ✅ 串口已检测到 reboot 命令")
                allure.attach("串口已检测到 reboot 命令", name="✅ 日志校验通过",
                              attachment_type=allure.attachment_type.TEXT)
            else:
                allure.attach("未在串口日志中检测到 reboot 关键字（可能日志截断）",
                              name="⚠️ 日志校验警告", attachment_type=allure.attachment_type.TEXT)
                print("[Test] ⚠️ 未检测到 reboot 关键字，继续验证...")

        # ========== 3. 等待设备启动 ==========
        with allure.step(f"等待设备重启完成（{self.REBOOT_WAIT_TIME} 秒）"):
            print(f"[Test] ⏳ 等待设备启动（{self.REBOOT_WAIT_TIME} 秒）...")
            self.home_page.ensure_back_to_home()
            time.sleep(self.REBOOT_WAIT_TIME)

            ready = serial_logger.ensure_logged_in(timeout=5)
            if ready:
                print("[Test] ✅ 设备串口已就绪")
                allure.attach("设备串口已就绪，可接收命令", name="✅ 设备启动完成",
                              attachment_type=allure.attachment_type.TEXT)
            else:
                print("[Test] ⚠️ 设备串口未就绪，继续尝试 UI 验证")

        # ========== 4. 尝试预览出图 ==========
        with allure.step("验证设备是否正常出图"):
            success = self._verify_live_stream(device_name, serial_logger)

        # ========== 5. 如果出图失败，通过串口执行 reboot 恢复 ==========
        if not success:
            with allure.step("出图失败，通过串口执行 reboot 命令恢复"):
                print("[Test] 🟢 通过串口执行 reboot 命令恢复设备...")
                serial_logger.send_cmd("reboot", timeout=2)
                time.sleep(10)
                print("[Test]  等待设备重新启动（90 秒）...")
                time.sleep(90)
                self.home_page.ensure_back_to_home()
                if self._try_live_stream(device_name, timeout=20):
                    print("[Test] ✅ 通过串口 reboot 后设备恢复正常")
                else:
                    print("[Test] ❌ 串口 reboot 后设备仍无法出图，需要人工介入")

        # ========== 6. 返回首页 ==========
        with allure.step("返回首页"):
            self.home_page.ensure_back_to_home()
            print("[Test] ✅ 已返回首页")

        # ========== 7. 最终断言 ==========
        assert success, f"设备 [{device_name}] 重启后无法出图，视为缺陷"

    def _try_live_stream(self, device_name: str, timeout: int = 15) -> bool:
        """单次尝试预览出图"""
        try:
            self.home_page.ensure_back_to_home()
            time.sleep(1)
            status = self.home_page.check_device_offline_status(device_name)
            if status.get("is_offline", False):
                return False
            self.home_page.click_play_button(device_name)
            time.sleep(2)
            return self.live_page.wait_for_stream_loaded(timeout=timeout)
        except Exception as e:
            print(f"[Test] ⚠️ 预览尝试失败: {e}")
            return False

    def _verify_live_stream(self, device_name: str, serial_logger) -> bool:
        """尝试预览出图，最多重试 MAX_RETRY 次"""
        for attempt in range(self.MAX_RETRY + 1):
            print(f"[Test]  第 {attempt + 1}/{self.MAX_RETRY + 1} 次尝试预览出图...")

            status = self.home_page.check_device_offline_status(device_name)
            if status.get("is_offline", False):
                print(f"[Test] ⚠️ 设备离线，尝试 {attempt + 1}")
                allure.attach(
                    f"设备 [{device_name}] 当前处于离线状态\n离线时间: {status.get('offline_time', '未知')}",
                    name=f"⚠️ 设备离线 (尝试 {attempt + 1})",
                    attachment_type=allure.attachment_type.TEXT
                )
                if attempt < self.MAX_RETRY:
                    time.sleep(self.RETRY_INTERVAL)
                    continue
                else:
                    return False

            if self._try_live_stream(device_name, timeout=15):
                print(f"[Test] ✅ 设备 [{device_name}] 重启成功，出图正常！")
                allure.attach(
                    f"设备 [{device_name}] 重启后出图正常，用时 {attempt + 1} 次尝试",
                    name="✅ 重启成功",
                    attachment_type=allure.attachment_type.TEXT
                )
                return True

            if attempt < self.MAX_RETRY:
                print(f"[Test]  出图失败，等待 {self.RETRY_INTERVAL} 秒后重试...")
                time.sleep(self.RETRY_INTERVAL)

        return False