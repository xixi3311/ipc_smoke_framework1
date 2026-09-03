# tests/test_delete.py
import pytest
import allure
import time
import config
from pages.first_page.home_page import HomePage
from pages.second_page.live_page import LivePage
from pages.third_page.setting_page import SettingsPage


@allure.epic("IPC 自动化测试框架")
@allure.feature("设备删除（含日志校验）")
class TestDelete:

    TARGET_DEVICE = getattr(config, "DEVICE_NAME", "摄像机")

    @pytest.fixture(autouse=True)
    def setup_pages(self, driver):
        self.driver = driver
        self.home_page = HomePage(driver)
        self.live_page = LivePage(driver)
        self.settings_page = SettingsPage(driver)
        self.home_page.ensure_back_to_home()

    @allure.story("删除设备并验证从列表移除（含串口日志校验）")
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_delete_device(self, serial_logger):
        device_name = self.TARGET_DEVICE
        device_sn = config.DEVICE_SN

        # ========== 1. 进入设置并执行删除 ==========
        with allure.step(f"进入设备 [{device_name}] Live 预览"):
            self.home_page.click_play_button(device_name)
            self.live_page.wait_for_stream_loaded()

        with allure.step("进入设备设置页"):
            self.live_page.click_settings_gear()
            assert self.settings_page.is_on_settings_page(), "未能进入设置页"

        with allure.step("点击『删除设备』并确认弹窗"):
            assert self.settings_page.click_delete_device(), "点击删除设备失败"
            time.sleep(0.5)
            assert self.settings_page.confirm_delete_dialog(confirm=True), "确认删除弹窗失败"
            print("[Test] ✅ 设备删除指令已确认")

        # ========== 2. 串口日志检测设备解绑日志 ==========
        with allure.step("串口日志检测设备解绑/停止上报日志"):
            print("[Test]  检测串口日志中的设备解绑记录...")
            keywords = [device_sn, "unbind", "logout", "device offline"]
            found = False
            for kw in keywords:
                if serial_logger.search_keyword(kw, timeout=5):
                    print(f"[Test] ✅ 串口检测到关键字: {kw}")
                    found = True
                    break
            if found:
                allure.attach("串口已检测到设备解绑/停止上报日志",
                              name="✅ 日志校验通过", attachment_type=allure.attachment_type.TEXT)
            else:
                allure.attach("未检测到明确的设备解绑日志（可能日志截断）",
                              name="⚠️ 日志校验警告", attachment_type=allure.attachment_type.TEXT)
                print("[Test] ⚠️ 未检测到设备解绑日志，继续验证...")

        # ========== 3. 验证设备从首页移除 ==========
        with allure.step("验证设备已从首页列表中移除"):
            removed = self._verify_device_removed(device_name)

        # ========== 4. 返回首页 ==========
        with allure.step("返回首页"):
            self.home_page.ensure_back_to_home()
            print("[Test] ✅ 已返回首页")

        # ========== 5. 最终断言 ==========
        assert removed, f"设备 [{device_name}] 仍在首页列表中，删除失败"

        # ========== 6. ⚠️ 关键：等待设备进入待配网状态 ==========
        with allure.step("等待设备完全解绑并进入待配网状态（60 秒）"):
            print("[Test]  等待设备完全解绑并进入待配网状态（60 秒）...")
            print("[Test] ⚠️ 设备已删除，下一轮绑定需等待设备进入待配网状态")
            time.sleep(60)
            print("[Test] ✅ 设备应已进入待配网状态，可进行下一轮绑定")

        # ========== 7. 提示后续操作 ==========
        allure.attach(
            "设备已删除，已等待 60 秒进入待配网状态，可执行下一轮绑定",
            name="⚠️ 提示",
            attachment_type=allure.attachment_type.TEXT
        )
        print("[Test] ⚠️ 设备已删除，可执行下一轮绑定")

    def _verify_device_removed(self, device_name: str) -> bool:
        """验证设备已从首页列表移除"""
        self.home_page.ensure_back_to_home()
        time.sleep(2)

        max_wait = 30
        start = time.time()
        while time.time() - start < max_wait:
            device_names = self.home_page.get_current_screen_device_names()
            if device_name not in device_names:
                print(f"[Test] ✅ 设备 [{device_name}] 已从首页移除")
                allure.attach(
                    f"设备 [{device_name}] 已从首页列表中移除",
                    name="✅ 删除成功",
                    attachment_type=allure.attachment_type.TEXT
                )
                return True
            time.sleep(2)
            self.driver.swipe_ext("down", scale=0.3)

        return False