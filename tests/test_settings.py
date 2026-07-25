import time
import allure
import pytest
from pages.first_page.home_page import HomePage
from pages.second_page.live_page import LivePage
from pages.third_page.setting_page import SettingsPage


@allure.epic("IPC 自动化测试框架")
@allure.feature("设备设置模块测试")
class TestDeviceSettings:

    TARGET_DEVICE = "2601P测"

    @pytest.fixture(autouse=True)
    def setup_page(self, driver):
        """用例前置：初始化 Page 对象并确保返回 App 首页"""
        self.driver = driver
        self.home_page = HomePage(driver)
        self.live_page = LivePage(driver)
        self.settings_page = SettingsPage(driver)

        # 确保启动用例前回到首页
        self.home_page.ensure_back_to_home()

    @allure.story("设备设置 - 进入设置界面校验 (UI1)")
    @pytest.mark.smoke
    def test_enter_device_settings(self):
        """测试从 Live 预览页点击右上角齿轮，能否正常进入设置界面"""
        with allure.step(f"进入 [{self.TARGET_DEVICE}] Live 预览"):
            self.home_page.click_play_button(self.TARGET_DEVICE)
            self.live_page.wait_for_stream_loaded()

        with allure.step("点击 Live 预览页右上角 '设置齿轮' 图标"):
            assert self.live_page.click_settings_gear(), "点击设置齿轮图标失败"
            time.sleep(1.0)

        with allure.step("校验是否成功进入设备设置界面"):
            assert self.settings_page.is_on_settings_page(), "未能成功进入设备设置界面！"

    @allure.story("设备设置 - 进入工作模式选择界面校验 (UI5)")
    @pytest.mark.smoke
    def test_enter_work_mode_page(self):
        """测试在设置界面点击『工作模式』整行，能否正常进入 UI5 工作模式选择页"""
        with allure.step(f"进入 [{self.TARGET_DEVICE}] Live 预览并跳转至设置页"):
            self.home_page.click_play_button(self.TARGET_DEVICE)
            self.live_page.wait_for_stream_loaded()
            self.live_page.click_settings_gear()
            time.sleep(1.0)

        with allure.step("确认处于设置界面"):
            assert self.settings_page.is_on_settings_page(), "未能成功进入设备设置界面"

        with allure.step("点击『工作模式』入口跳转 UI5"):
            assert self.settings_page.click_work_mode_entry(), "点击工作模式整行失败"
            time.sleep(1.0)

        with allure.step("校验是否成功处于工作模式选择界面 (UI5)"):
            assert self.settings_page.is_on_work_mode_page(), "未能成功进入工作模式选择界面 (UI5)！"

    @allure.story("设备设置 - 执行设备重启功能校验 (UI2 -> UI3)")
    @pytest.mark.smoke
    def test_reboot_device_flow(self):
        """测试在设置页滑动到底部点击『重启设备』，并确认二次弹窗下发重启指令"""
        with allure.step(f"进入 [{self.TARGET_DEVICE}] Live 预览并跳转至设置页"):
            self.home_page.click_play_button(self.TARGET_DEVICE)
            self.live_page.wait_for_stream_loaded()
            self.live_page.click_settings_gear()
            time.sleep(1.0)

        with allure.step("确认处于设置界面"):
            assert self.settings_page.is_on_settings_page(), "未能成功进入设备设置界面"

        with allure.step("自动向下滑动到底部并点击『重启设备』按钮"):
            assert self.settings_page.click_reboot_device(), "寻找/点击『重启设备』按钮失败"

        with allure.step("点击重启弹窗中的『确定』按键 (UI3)"):
            assert self.settings_page.confirm_reboot_dialog(), "确认重启弹窗操作失败"
            print("[Test] 🟢 设备重启指令下发成功！")

    @allure.story("设备设置 - 删除设备弹窗交互校验 (点击取消)")
    @pytest.mark.smoke
    def test_delete_device_dialog_cancel(self):
        """测试滑动到底部点击删除设备，弹出 UI4 确认框后点击取消，不破坏设备状态"""
        with allure.step(f"进入 [{self.TARGET_DEVICE}] Live 预览并跳转至设置页"):
            self.home_page.click_play_button(self.TARGET_DEVICE)
            self.live_page.wait_for_stream_loaded()
            self.live_page.click_settings_gear()
            time.sleep(1.0)

        with allure.step("向下滑动到底部并点击『删除设备』"):
            assert self.settings_page.click_delete_device(), "点击『删除设备』失败"
            time.sleep(0.5)

        with allure.step("在删除弹窗中点击『取消』(安全退出)"):
            assert self.settings_page.confirm_delete_dialog(confirm=False), "点击取消删除失败"
            print("[Test] 🟢 成功验证删除设备弹窗交互（已安全取消，未解绑设备）")