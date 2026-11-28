import time
import allure
import pytest
import config
from pages.first_page.home_page import HomePage
from pages.second_page.live_page import LivePage
from pages.third_page.setting_page import SettingsPage
from pages.fourth_page.work_mode_page import WorkModePage
from pages.fourth_page.camera_settings_page import CameraSettingsPage
from pages.fifth_page.image_flip_page import ImageFlipPage


@allure.epic("IPC 自动化测试框架")
@allure.feature("画面翻转测试")
class TestImageFlip:
    TARGET_DEVICE = config.DEVICE_NAME

    @pytest.fixture(autouse=True)
    def setup_page(self, driver):
        self.driver = driver
        self.home_page = HomePage(driver)
        self.live_page = LivePage(driver)
        self.settings_page = SettingsPage(driver)
        self.work_mode_page = WorkModePage(driver)
        self.camera_settings_page = CameraSettingsPage(driver)
        self.image_flip_page = ImageFlipPage(driver)

        self.home_page.ensure_back_to_home()

    @allure.story("绑定后切换常电模式并开启画面翻转")
    @pytest.mark.smoke
    def test_enable_image_flip(self):
        with allure.step("进入预览并确认画面出图"):
            assert self.home_page.click_play_button(
                self.TARGET_DEVICE
            ), "进入 Live 预览失败"
            assert self.live_page.wait_for_stream_loaded(), \
                "Live 画面未成功出图"

        if config.DEVICE_WORK_MODE.strip().upper() == "AOV":
            with allure.step("进入设置并切换为常电模式"):
                assert self.live_page.click_settings_gear(), \
                    "进入设备设置失败"
                assert self.settings_page.click_work_mode_entry(), \
                    "进入工作模式页面失败"
                assert self.work_mode_page.is_on_work_mode_page(), \
                    "未能进入工作模式页面"
                assert self.work_mode_page.select_mode("常电模式"), \
                    "切换常电模式失败"
                assert self.work_mode_page.click_back_to_settings(), \
                    "返回设备设置页失败"
                assert self.home_page.ensure_back_to_home(), \
                    "切换工作模式后返回首页失败"
                time.sleep(0.5)
        else:
            print("[Test] 常电设备跳过工作模式切换")



        with allure.step("重新进入预览并打开设备设置"):
            assert self.home_page.click_play_button(
                self.TARGET_DEVICE
            ), "重新进入 Live 预览失败"
            assert self.live_page.wait_for_stream_loaded(), \
                "Live 画面未成功出图"
            assert self.live_page.click_settings_gear(), \
                "进入设备设置失败"

        with allure.step("查找并进入摄像机设置"):
            entry_visible_first = \
                self.settings_page.is_camera_settings_entry_visible()
            print(
                "[SettingsPage] 首次进入设置时，"
                f"摄像机设置入口可见: {entry_visible_first}"
            )

            assert self.settings_page.click_camera_settings_entry(), \
                "滑动查找或点击摄像机设置入口失败"
            assert self.camera_settings_page.is_on_camera_settings_page(), \
                "未能进入摄像机设置页"
            assert self.camera_settings_page.is_image_flip_status_unflipped(), \
                "摄像机设置页的画面翻转状态不是“未翻转”"

        with allure.step("进入画面翻转页并切换为翻转"):
            assert self.camera_settings_page.click_image_flip_entry(), \
                "点击画面翻转入口失败"
            assert self.image_flip_page.is_on_image_flip_page(), \
                "未能进入画面翻转页面"
            assert self.image_flip_page.is_unflipped_selected(), \
                "绑定后的初始状态不是未翻转"
            assert self.image_flip_page.select_flipped(), \
                "选择画面翻转失败"
            assert self.image_flip_page.is_flipped_selected(), \
                "画面翻转没有显示为选中"
            assert not self.image_flip_page.is_unflipped_selected(), \
                "画面不翻转仍显示为选中"

        with allure.step("返回首页"):
            assert self.image_flip_page.click_back(), \
                "从画面翻转页返回失败"
            assert self.camera_settings_page.is_on_camera_settings_page(), \
                "未返回摄像机设置页"
            assert self.camera_settings_page.click_back(), \
                "从摄像机设置页返回失败"
            assert self.home_page.ensure_back_to_home(), \
                "最终未能返回首页"