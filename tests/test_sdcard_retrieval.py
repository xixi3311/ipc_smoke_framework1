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

    @allure.story("卡回看检索：事件类型切换、随机事件播放和日期切换验证")
    @pytest.mark.smoke
    def test_sdcard_retrieval_flow(self):
        """验证 SD 卡录像检索及有人、车辆事件回放"""

        device_name = self.TARGET_DEVICE

        # 每次用例开始时初始化备注，供 conftest.py 写入 Excel
        self.result_remark = ""

        # ---- 步骤 1：切换常电模式 ----
        with allure.step("切换设备工作模式为常电模式"):
            assert self.home_page.click_play_button(device_name), \
                "点击播放按钮失败，未进入 Live 页面"
            assert self.live_page.wait_for_stream_loaded(), \
                "Live 预览未能正常出图"
            assert self.live_page.click_settings_gear(), \
                "点击设置齿轮失败"
            assert self.settings_page.click_work_mode_entry(), \
                "点击工作模式入口失败"
            assert self.work_mode_page.select_mode("常电模式"), \
                "切换常电模式失败"

            self.work_mode_page.click_back_to_settings()
            self.settings_page.click_back_to_live()
            self.live_page.click_back_to_home()
            assert self.home_page.ensure_back_to_home(), \
                "未能返回设备首页"
            time.sleep(2)

        # ---- 步骤 2：进入卡回看页面 ----
        with allure.step("从首页进入 Live 预览"):
            assert self.home_page.click_play_button(device_name), \
                "点击播放按钮失败，未进入 Live 页面"
            assert self.live_page.wait_for_stream_loaded(), \
                "Live 预览未能正常出图"

        with allure.step("进入卡回看页面"):
            assert self.live_page.click_card_playback(), \
                "点击卡回放按钮失败"
            time.sleep(1.5)

        # 没有任何 SD 卡录像时，整条检索用例跳过
        if not self.sdcard_ext_page.has_sd_card_video():
            self.result_remark = "设备未检索到 SD 卡录像"
            pytest.skip("设备未检索到 SD 卡录像，跳过检索验证")

        # ---- 步骤 3：检索有人和有车事件录像 ----
        with allure.step("扫描设备支持的事件类型"):
            available_types = self.sdcard_ext_page.scan_available_event_types()

            assert available_types, "未扫描到任何事件类型"

            allure.attach(
                str(available_types),
                name="支持的事件类型",
                attachment_type=allure.attachment_type.TEXT
            )

            # 只检查有人出现和有车出现两类事件
            event_types = [
                event_type for event_type in available_types
                if event_type in ("有人出现", "有车出现")
            ]

            # 记录无录像类别、存在录像类别和成功回放类别
            no_video_types = []
            video_types = []
            success_types = []
            failed_types = []

            for event_type in event_types:
                with allure.step(f"切换到事件类型：{event_type}"):
                    assert self.sdcard_ext_page.select_event_type(event_type), \
                        f"切换到 {event_type} 失败"
                    time.sleep(1)

                # 当前筛选列表为空，说明该类别没有检索到录像
                event_items = self.sdcard_ext_page._get_event_items()
                if not event_items:
                    no_video_types.append(event_type)
                    print(
                        f"[Test] {event_type} 未检索到录像，"
                        "跳过该类别"
                    )
                    continue

                video_types.append(event_type)

                # 当前类别有录像，随机播放并校验
                with allure.step(
                    f"验证事件类型 [{event_type}] 的录像回放"
                ):
                    result = (
                        self.sdcard_ext_page
                        .click_random_events_and_verify(count=2)
                    )

                if result:
                    success_types.append(event_type)
                else:
                    failed_types.append(event_type)
                    print(
                        f"[Test] {event_type} 检索到录像，"
                        "但回放验证失败"
                    )

            # 将分类结果写入当前测试实例，供 conftest.py 读取并导出到备注
            remark_parts = []

            if no_video_types:
                remark_parts.append(
                    f"未检索到录像：{'、'.join(no_video_types)}"
                )

            if success_types:
                remark_parts.append(
                    f"回放成功：{'、'.join(success_types)}"
                )

            if failed_types:
                remark_parts.append(
                    f"回放验证失败：{'、'.join(failed_types)}"
                )

            self.result_remark = "；".join(remark_parts)

            # 设备没有提供有人/有车事件类型时，不作为失败
            if not event_types:
                self.result_remark = (
                    "设备未提供有人出现或有车出现事件类型"
                )
                pytest.skip(self.result_remark)

            # 有人或有车任一类别的录像成功回放，即认为 SD 卡回看通过
            if success_types:
                print(
                    "[Test] SD 卡回看验证通过，成功类别："
                    f"{'、'.join(success_types)}"
                )

            # 找到了录像但所有类别都回放失败，才判定测试失败
            elif video_types:
                assert False, (
                    "已检索到有人或有车录像，"
                    "但所有有录像类别的回放验证均失败"
                )

            # 有人和有车都没有录像，属于无可检索事件，跳过而非失败
            else:
                pytest.skip(
                    "有人出现和有车出现均未检索到录像；"
                    f"备注：{self.result_remark}"
                )

        # ---- 步骤 4: 回到首页 ----
        with allure.step("返回首页"):
            self.sdcard_ext_page.click_back_to_live()
            self.live_page.click_back_to_home()
            self.home_page.ensure_back_to_home()