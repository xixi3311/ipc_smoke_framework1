# tests/test_work_mode.py
import time
import allure
import pytest
from pages.first_page.home_page import HomePage
from pages.second_page.live_page import LivePage
from pages.third_page.setting_page import SettingsPage
from pages.fourth_page.work_mode_page import WorkModePage


@allure.epic("IPC 自动化测试框架")
@allure.feature("工作模式模块测试")
class TestWorkMode:
    TARGET_DEVICE = "5556测AOV"

    @pytest.fixture(autouse=True)
    def setup_page(self, driver):
        """用例前置：初始化 Page 对象并确保返回 App 首页"""
        self.driver = driver
        self.home_page = HomePage(driver)
        self.live_page = LivePage(driver)
        self.settings_page = SettingsPage(driver)
        self.work_mode_page = WorkModePage(driver)

        # 确保启动用例前回到首页
        self.home_page.ensure_back_to_home()

    @allure.story("工作模式 - 动态遍历设备支持的所有模式并切回 Live 验证")
    @pytest.mark.smoke
    def test_switch_all_available_work_modes(self):
        """测试动态获取设备支持的所有工作模式，逐个精准点击切换并验证 Live 画面"""

        # 1. 首次进入工作模式页面
        self.home_page.click_play_button(self.TARGET_DEVICE)
        self.live_page.wait_for_stream_loaded()
        self.live_page.click_settings_gear()
        self.settings_page.click_work_mode_entry()

        assert self.work_mode_page.is_on_work_mode_page(), "未能成功进入工作模式选择界面！"

        # 动态扫描当前设备支持的模式列表
        available_modes = self.work_mode_page.get_available_modes()
        assert len(available_modes) > 0, "未在页面上扫描到任何有效的工作模式！"

        for mode_name in available_modes:
            with allure.step(f"切换工作模式为: [{mode_name}]"):
                # 确保当前处于工作模式页面
                if not self.work_mode_page.is_on_work_mode_page():
                    # 如果在 Live 页面，先点击齿轮
                    if self.live_page.is_on_live_page():
                        self.live_page.click_settings_gear()
                        time.sleep(1.0)
                    # 如果在设置页面，点击工作模式入口
                    if self.settings_page.is_on_settings_page():
                        self.settings_page.click_work_mode_entry()
                        time.sleep(1.0)

                # 精准点击 RadioButton 切换模式
                switch_res = self.work_mode_page.select_mode(mode_name)
                assert switch_res, f"切换到工作模式 [{mode_name}] 失败！"

                # 步骤 C: 工作模式页 -> 返回设置页 -> 返回 Live 界面校验
                self.work_mode_page.click_back_to_settings()
                time.sleep(1.0)
                self.settings_page.click_back_to_live()
                time.sleep(1.0)

                # 验证 Live 画面出图
                assert self.live_page.wait_for_stream_loaded(), f"切换模式 [{mode_name}] 后 Live 画面未正常出图！"