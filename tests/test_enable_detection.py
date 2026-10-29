import allure
import pytest
import config
from pages.first_page.home_page import HomePage
from pages.second_page.live_page import LivePage
from pages.third_page.setting_page import SettingsPage
from pages.fourth_page.detection_page import DetectionPage
from pages.fifth_page.detection_event_page import DetectionEventPage


@allure.epic("IPC 自动化测试框架")
@allure.feature("智能侦测")
class TestEnableDetection:
    TARGET_DEVICE = config.DEVICE_NAME

    @pytest.fixture(autouse=True)
    def setup_page(self, driver):
        self.driver = driver
        self.home_page = HomePage(driver)
        self.live_page = LivePage(driver)
        self.settings_page = SettingsPage(driver)
        self.detection_page = DetectionPage(driver)
        self.detection_event_page = DetectionEventPage(driver)

        self.home_page.ensure_back_to_home()

    @allure.story("调试开启有车出现侦测")
    def test_enable_detection(self):
        with allure.step("进入设备预览并打开设置"):
            assert self.home_page.click_play_button(
                self.TARGET_DEVICE
            ), "进入 Live 预览失败"
            assert self.live_page.wait_for_stream_loaded(), \
                "Live 画面未成功出图"
            assert self.live_page.click_settings_gear(), \
                "进入设备设置失败"

        with allure.step("进入智能侦测并确认初始状态"):
            assert self.settings_page.click_intelligent_detection_entry(), \
                "点击智能侦测入口失败"
            assert self.detection_page.is_on_detection_page(), \
                "未能进入智能侦测页面"
            assert self.detection_page.is_person_detection_enabled(), \
                "有人出现事件不是已开启状态"
            assert self.detection_page.is_car_detection_disabled(), \
                "有车出现事件初始状态不是未开启"
            assert self.detection_page.click_car_event(), \
                "点击有车出现事件失败"

        with allure.step("开启有车出现侦测"):
            assert self.detection_event_page.is_on_detection_event_page(), \
                "未能进入侦测事件详情页"
            assert self.detection_event_page.enable_detection(), \
                "开启侦测事件失败"
            assert self.detection_event_page.is_detection_enabled(), \
                "侦测开关没有显示为开启"

        with allure.step("返回首页"):
            assert self.detection_event_page.click_back(), \
                "返回智能侦测页面失败"
            assert self.detection_page.is_on_detection_page(), \
                "未返回智能侦测页面"
            assert self.detection_page.click_back(), \
                "返回设备设置页失败"
            assert self.home_page.ensure_back_to_home(), \
                "最终未能返回首页"