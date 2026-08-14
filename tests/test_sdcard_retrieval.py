# tests/test_sdcard_retrieval.py
import pytest
import allure
import time
import config
from pages.first_page.home_page import HomePage
from pages.second_page.live_page import LivePage
from pages.third_page.sdcard_replay_ext_page import SdCardReplayExtPage
from pages.third_page.setting_page import SettingsPage
from pages.fourth_page.work_mode_page import WorkModePage


@allure.epic("IPC 自动化测试框架")
@allure.feature("SD 卡回看检索与出图验证")
class TestSdCardRetrieval:

    TARGET_DEVICE = getattr(config, "DEVICE_NAME", "摄像机")

    @pytest.fixture(autouse=True)
    def setup_pages(self, driver):
        self.driver = driver
        self.home_page = HomePage(driver)
        self.live_page = LivePage(driver)
        self.settings_page = SettingsPage(driver)
        self.work_mode_page = WorkModePage(driver)
        self.sdcard_ext_page = SdCardReplayExtPage(driver)
        self.home_page.ensure_back_to_home()

    @allure.story("卡回看检索：事件类型切换 + 随机事件点击 + 随机日期切换 验证出图")
    @pytest.mark.smoke
    def test_sdcard_retrieval_flow(self):
        device_name = self.TARGET_DEVICE

        # ---- 步骤 1: 切换常电模式 ----
        with allure.step("切换设备工作模式为『常电模式』"):
            self.home_page.click_play_button(device_name)
            self.live_page.wait_for_stream_loaded()
            self.live_page.click_settings_gear()
            self.settings_page.click_work_mode_entry()
            self.work_mode_page.select_mode("常电模式")
            self.work_mode_page.click_back_to_settings()
            self.settings_page.click_back_to_live()
            self.live_page.click_back_to_home()
            self.home_page.ensure_back_to_home()
            time.sleep(2)

        # ---- 步骤 2: 进入卡回看界面 ----
        with allure.step("从首页点击设备播放，进入 Live 预览"):
            self.home_page.click_play_button(device_name)
            self.live_page.wait_for_stream_loaded()

        with allure.step("点击底部『卡回放』进入卡回看页面"):
            self.live_page.click_card_playback()
            time.sleep(1.5)

        # 判断是否有录像
        if not self.sdcard_ext_page.has_sd_card_video():
            pytest.skip("该设备无 SD 卡录像，跳过检索验证")

        # ---- 步骤 3: 扫描并切换事件类型，随机点击事件 ----
        with allure.step("扫描设备支持的事件类型"):
            available_types = self.sdcard_ext_page.scan_available_event_types()
            assert len(available_types) > 0, "未扫描到任何事件类型"
            allure.attach(str(available_types), name="支持的事件类型", attachment_type=allure.attachment_type.TEXT)

            filter_types = [t for t in available_types if t != "全部录像"]
            if not filter_types:
                self.logger.warning("设备仅支持『全部录像』，跳过事件类型切换测试")
            else:
                for event_type in filter_types:
                    with allure.step(f"切换到事件类型: {event_type}"):
                        assert self.sdcard_ext_page.select_event_type(event_type), f"切换 {event_type} 失败"
                        time.sleep(1)

                    with allure.step(f"在当前类型 [{event_type}] 中随机点击 2 个事件并验证出图"):
                        result = self.sdcard_ext_page.click_random_events_and_verify(count=2)
                        assert result, f"在类型 {event_type} 下事件点击验证失败"

        # ---- 步骤 4: 回到首页 ----
        with allure.step("返回首页"):
            self.sdcard_ext_page.click_back_to_live()
            self.live_page.click_back_to_home()
            self.home_page.ensure_back_to_home()