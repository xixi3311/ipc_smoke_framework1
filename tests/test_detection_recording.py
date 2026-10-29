import time
import allure
import pytest
import config
from pages.first_page.home_page import HomePage
from pages.second_page.live_page import LivePage
from pages.third_page.setting_page import SettingsPage
from pages.fourth_page.camera_settings_page import CameraSettingsPage
from pages.fourth_page.detection_page import DetectionPage
from pages.fifth_page.image_flip_page import ImageFlipPage
from pages.fifth_page.detection_event_page import DetectionEventPage


@allure.epic("IPC 自动化测试框架")
@allure.feature("侦测事件录像")
class TestDetectionRecording:
    TARGET_DEVICE = config.DEVICE_NAME
    DETECTION_DURATION = 60

    @pytest.fixture(autouse=True)
    def setup_pages(self, driver):
        self.driver = driver
        self.home_page = HomePage(driver)
        self.live_page = LivePage(driver)
        self.settings_page = SettingsPage(driver)
        self.camera_settings_page = CameraSettingsPage(driver)
        self.image_flip_page = ImageFlipPage(driver)
        self.detection_page = DetectionPage(driver)
        self.detection_event_page = DetectionEventPage(driver)

        self.home_page.ensure_back_to_home()

    @allure.story("开启翻转和车型侦测后持续预览一分钟")
    @pytest.mark.smoke
    def test_detection_recording(self):
        with allure.step("进入预览并打开设备设置"):
            assert self.home_page.click_play_button(
                self.TARGET_DEVICE
            ), "进入 Live 预览失败"
            assert self.live_page.wait_for_stream_loaded(), \
                "Live 画面未成功出图"
            assert self.live_page.click_settings_gear(), \
                "进入设备设置失败"

        with allure.step("确保画面翻转已开启"):
            assert self.settings_page.click_camera_settings_entry(), \
                "查找或点击摄像机设置入口失败"
            assert self.camera_settings_page.is_on_camera_settings_page(), \
                "未能进入摄像机设置页"
            assert self.camera_settings_page.click_image_flip_entry(), \
                "点击画面翻转入口失败"
            assert self.image_flip_page.is_on_image_flip_page(), \
                "未能进入画面翻转页面"
            assert self.image_flip_page.select_flipped(), \
                "开启画面翻转失败"
            assert self.image_flip_page.is_flipped_selected(), \
                "画面翻转没有显示为选中"
            assert self.image_flip_page.click_back(), \
                "从画面翻转页返回失败"
            assert self.camera_settings_page.is_on_camera_settings_page(), \
                "未返回摄像机设置页"
            assert self.camera_settings_page.click_back(), \
                "从摄像机设置页返回失败"

        with allure.step("确保车型侦测已开启"):
            assert self.settings_page.click_intelligent_detection_entry(), \
                "点击智能侦测入口失败"
            assert self.detection_page.is_on_detection_page(), \
                "未能进入智能侦测页面"
            assert self.detection_page.click_car_event(), \
                "点击有车出现事件失败"
            assert self.detection_event_page.is_on_detection_event_page(), \
                "未能进入有车出现设置页"
            assert self.detection_event_page.enable_detection(), \
                "开启车型侦测失败"
            assert self.detection_event_page.is_detection_enabled(), \
                "车型侦测开关没有显示为开启"
            assert self.detection_event_page.click_back(), \
                "从有车出现设置页返回失败"
            assert self.detection_page.is_on_detection_page(), \
                "未返回智能侦测页面"
            assert self.detection_page.click_back(), \
                "从智能侦测页面返回失败"
            assert self.home_page.ensure_back_to_home(), \
                "未能返回设备首页"

        with allure.step("回到预览并持续触发侦测一分钟"):
            assert self.home_page.click_play_button(
                self.TARGET_DEVICE
            ), "重新进入 Live 预览失败"
            assert self.live_page.wait_for_stream_loaded(), \
                "Live 画面未成功出图"

            print(
                f"[Test] 开始持续触发人形和车型侦测，"
                f"等待 {self.DETECTION_DURATION} 秒"
            )
            time.sleep(self.DETECTION_DURATION)
            print("[Test] 一分钟侦测触发完成")