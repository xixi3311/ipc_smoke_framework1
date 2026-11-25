import allure
import pytest
import config
from pages.first_page.home_page import HomePage
from pages.second_page.live_page import LivePage
from pages.third_page.setting_page import SettingsPage
from pages.fourth_page.sdcard_storage_page import SdCardStoragePage


@allure.epic("IPC 自动化测试框架")
@allure.feature("SD 卡格式化")
class TestSdCardFormat:
    TARGET_DEVICE = config.DEVICE_NAME

    @pytest.fixture(autouse=True)
    def setup_pages(self, driver):
        self.driver = driver
        self.home_page = HomePage(driver)
        self.live_page = LivePage(driver)
        self.settings_page = SettingsPage(driver)
        self.sdcard_storage_page = SdCardStoragePage(driver)
        self.home_page.ensure_back_to_home()

    @allure.story("格式化 SD 卡并返回首页")
    @pytest.mark.smoke
    def test_format_sd_card(self):
        home_returned = False

        try:
            with allure.step("进入预览并打开设置"):
                assert self.home_page.click_play_button(
                    self.TARGET_DEVICE
                ), "进入 Live 预览失败"
                assert self.live_page.wait_for_stream_loaded(), \
                    "Live 画面未成功出图"
                assert self.live_page.click_settings_gear(), \
                    "进入设备设置失败"

            with allure.step("检查并进入 SD 卡存储空间"):
                status = self.settings_page.get_sd_storage_status()
                assert status, "未读取到存储空间状态"
                assert status != "未接入", "SD 卡未接入"

                assert self.settings_page.click_sd_storage_entry(), \
                    "点击存储空间入口失败"
                assert self.sdcard_storage_page.is_on_storage_page(), \
                    "未能进入存储空间页面"

            with allure.step("确认并执行格式化"):
                assert self.sdcard_storage_page.click_format(), \
                    "点击格式化失败"
                assert self.sdcard_storage_page.is_format_confirm_dialog_visible(), \
                    "未出现确认格式化弹窗"
                assert self.sdcard_storage_page.confirm_format(), \
                    "确认格式化失败"

            with allure.step("等待格式化完成"):
                result = self.sdcard_storage_page.wait_for_format_result(
                    timeout=90
                )

                if result == "failed":
                    assert self.sdcard_storage_page.click_format_failed_cancel(), \
                        "格式化失败后点击取消失败"
                    assert False, "SD 卡格式化失败，不重试"

                assert result == "success", \
                    "SD 卡格式化等待超过 90 秒仍未完成"
                assert self.sdcard_storage_page.click_format_success_confirm(), \
                    "格式化完成后点击“知道了”失败"

        finally:
            home_returned = self.home_page.ensure_back_to_home()
            if not home_returned:
                print("[Test] ⚠️ 未能通过首页恢复逻辑返回首页")

        assert home_returned, "本轮结束时未能返回首页"