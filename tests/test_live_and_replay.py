# tests/test_live_and_replay.py
import pytest
import allure
import time
from pages.first_page.home_page import HomePage
from pages.second_page.live_page import LivePage
from pages.third_page.sdcard_replay_page import SdCardReplayPage
from pages.third_page.cloud_replay_page import CloudReplayPage
from pages.third_page.setting_page import SettingsPage


@allure.epic("IPC 自动化测试框架")
@allure.feature("Live 实时预览与卡/云回看功能测试")
class TestLiveAndReplay:

    TARGET_DEVICE = "2601P测"

    @pytest.fixture(autouse=True)
    def setup_page(self, driver):
        self.driver = driver
        self.home_page = HomePage(driver)
        self.live_page = LivePage(driver)
        self.sdcard_page = SdCardReplayPage(driver)
        self.cloud_page = CloudReplayPage(driver)
        self.settings_page = SettingsPage(driver)

        # 确保启动时处于首页
        self.home_page.ensure_back_to_home()

    @allure.story("Live 预览界面出图校验")
    @pytest.mark.smoke
    def test_live_stream_display(self):
        with allure.step(f"从首页点击设备 [{self.TARGET_DEVICE}] 的 ▶️ 按钮"):
            assert self.home_page.click_play_button(self.TARGET_DEVICE), "点击播放按钮失败"

        with allure.step("验证 Live 画面是否成功出图 (支持1/2/3/4目)"):
            assert self.live_page.wait_for_stream_loaded(), "Live 实时画面出图失败！"

    @allure.story("设备设置 - 进入设置界面校验")
    @pytest.mark.smoke
    def test_enter_device_settings(self):
        """测试从 Live 预览页点击右上角齿轮，能否正常进入设置界面"""
        with allure.step(f"进入 [{self.TARGET_DEVICE}] Live 预览"):
            self.home_page.click_play_button(self.TARGET_DEVICE)
            self.live_page.wait_for_stream_loaded()

        with allure.step("点击 Live 预览页右上角 '设置齿轮' 图标"):
            assert self.live_page.click_settings_gear(), "点击设置齿轮图标失败"
            time.sleep(1.0)  # 预留页面动画跳转时间

        with allure.step("校验是否成功进入设备设置界面"):
            assert self.settings_page.is_on_settings_page(), "未能成功进入设备设置界面！"

    @allure.story("卡回看 (SD Card) 切换与出图校验")
    @pytest.mark.smoke
    def test_sdcard_replay_display(self):
        with allure.step(f"进入 [{self.TARGET_DEVICE}] Live 预览"):
            self.home_page.click_play_button(self.TARGET_DEVICE)
            self.live_page.wait_for_stream_loaded()

        with allure.step("点击底部 '卡回放'"):
            assert self.live_page.click_card_playback(), "点击卡回放按钮失败"

        with allure.step("验证卡回看画面出图状态"):
            assert self.sdcard_page.wait_for_stream_loaded(), "卡回看视频出图失败！"

            # ---- 步骤 4: 回到首页 ----
            with allure.step("返回首页"):
                self.sdcard_ext_page.click_back_to_live()
                self.live_page.click_back_to_home()
                self.home_page.ensure_back_to_home()


"""
    @allure.story("云回看 (Cloud) 列表查看与视频播放出图校验")
    @pytest.mark.smoke
    def test_cloud_replay_display(self):
        with allure.step(f"进入 [{self.TARGET_DEVICE}] Live 预览"):
            self.home_page.click_play_button(self.TARGET_DEVICE)
            self.live_page.wait_for_stream_loaded()

        with allure.step("点击底部 '云回放' 进入 UI4 事件列表"):
            assert self.live_page.click_cloud_playback(), "点击云回放按钮失败"
            time.sleep(1)
            assert self.cloud_page.is_on_cloud_list_page(), "未能进入云回看事件列表界面 (UI4)"

        with allure.step("点击列表中的第一个云视频，跳转至 UI5"):
            assert self.cloud_page.click_first_event_item(), "点击云事件列表项失败"

        with allure.step("验证 UI5 云回看视频是否出图"):
            assert self.cloud_page.wait_for_stream_loaded(), "云视频播放出图失败！"


            # ---- 步骤 4: 回到首页 ----
            with allure.step("返回首页"):
                self.sdcard_ext_page.click_back_to_live()
                self.live_page.click_back_to_home()
                self.home_page.ensure_back_to_home()
"""

