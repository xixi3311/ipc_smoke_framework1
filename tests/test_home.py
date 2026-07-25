# tests/test_home.py
import pytest
import allure
import time
from pages.first_page.home_page import HomePage


@allure.epic("IPC 自动化测试框架")
@allure.feature("首页 UI 元素与功能验证")
class TestHomePage:
    TARGET_DEVICE = "2601P测"

    @pytest.fixture(autouse=True)
    def setup_page(self, driver):
        self.home_page = HomePage(driver)
        self.home_page.ensure_back_to_home()

    @allure.story("设备状态校验与播放预览")
    @pytest.mark.smoke
    def test_device_status_and_play(self):
        with allure.step(f"检查设备 [{self.TARGET_DEVICE}] 的在线/离线状态"):
            offline_info = self.home_page.check_device_offline_status(self.TARGET_DEVICE)

        with allure.step(f"验证设备 [{self.TARGET_DEVICE}] 点击 ▶️ 播放按钮"):
            if offline_info["is_offline"]:
                pytest.skip(f"设备 [{self.TARGET_DEVICE}] 处于离线状态，跳过播放测试！")
            else:
                assert self.home_page.click_play_button(self.TARGET_DEVICE), "点击播放按钮失败"
                time.sleep(2)

    @allure.story("右上角 '+' 号菜单点击测试")
    @pytest.mark.smoke
    def test_top_plus_menu(self):
        with allure.step("测试点击 '添加设备'"):
            assert self.home_page.open_add_device(), "点击 '添加设备' 失败"
            time.sleep(1)
            self.home_page.ensure_back_to_home()

        with allure.step("测试点击 '扫一扫'"):
            assert self.home_page.open_scan_qr(), "点击 '扫一扫' 失败"
            time.sleep(1)

    @allure.story("设备卡片 '⋮' 竖点与 '设置' 菜单验证")
    @pytest.mark.smoke
    def test_device_more_menu(self):
        with allure.step(f"点击设备 [{self.TARGET_DEVICE}] 右下角 '⋮' 按钮"):
            assert self.home_page.click_device_more_menu(self.TARGET_DEVICE), "点击 '⋮' 按钮失败"

        with allure.step("校验弹出菜单并点击 '设置'"):
            assert self.home_page.check_more_menu_settings_exist(), "弹出菜单中未找到 '设置' 选项"
            assert self.home_page.click_more_menu_settings(), "点击 '设置' 选项失败"
            time.sleep(1)