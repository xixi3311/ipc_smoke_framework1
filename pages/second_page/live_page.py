# pages/second_page/live_page.py
import time
import config
from pages.base_page import BasePage
from locators.second_page_locator.live_locator import LiveLocators
from locators.third_page_locator.setting_locator import SettingsLocators


class LivePage(BasePage):
    """Live 实时预览页面类"""

    # ---------------- 页面状态判断 ----------------
    def is_on_live_page(self) -> bool:
        """校验当前是否处于 Live 预览页面"""
        return (
            self._is_element_present(*LiveLocators.TV_CARD_PLAYBACK)
            or self._is_element_present(*LiveLocators.BTN_SETTINGS)
        )

    def is_loading(self) -> bool:
        """检查 Live 页面是否仍显示加载控件"""
        return self._is_element_present(*LiveLocators.LOADING_LAYOUT)

    def is_video_ready(self) -> bool:
        """
        判断 Live 是否真正出图。

        播放器容器存在不代表视频已经出图，
        还需要确认 Live 页面存在且 loading 控件已经消失。
        """

        return (
            self.is_on_live_page()
            and self._is_element_present(*LiveLocators.VIDEO_CONTAINER)
            and not self.is_loading()
        )

    # ---------------- Live 出图检测 ----------------
    def wait_for_stream_loaded(self, timeout: int = None) -> bool:
        """兼容原接口，返回 Live 是否出图"""
        success, _ = self.wait_for_stream_loaded_with_time(timeout=timeout)
        return success

    def wait_for_stream_loaded_with_time(self, timeout: int = None):
        """
        检测 Live 画面出图并记录耗时。

        连续三次检测到播放器就绪，才确认加载成功，
        避免 loading 状态短暂消失时误判为成功。
        """

        if timeout is None:
            timeout = getattr(config, "PREVIEW_TIMEOUT", 30)

        print(
            f"[LivePage] ⏳ 开始检测 Live 画面出图状态，"
            f"最长等待 {timeout} 秒..."
        )

        start_time = time.time()
        stable_count = 0

        while time.time() - start_time < timeout:
            if self.is_video_ready():
                stable_count += 1

                # 连续确认三次，降低加载状态切换造成的误判
                if stable_count >= 3:
                    duration = round(time.time() - start_time, 2)
                    print(
                        f"[LivePage] ✅ Live 画面加载成功！"
                        f"真实出图耗时: {duration} 秒"
                    )

                    # 保留原有停留时间，便于目测确认画面
                    print("[LivePage] 停留 2.0 秒以便目测确认出图画面...")
                    time.sleep(2.0)
                    return True, duration
            else:
                # loading 重新出现时，从头累计稳定次数
                stable_count = 0

            time.sleep(0.3)

        total_duration = round(time.time() - start_time, 2)
        print(
            f"[LivePage] ❌ Live 画面加载超时 ({timeout}s)，"
            "未能成功出图！"
        )
        return False, total_duration

    # ---------------- Live 页面操作 ----------------
    def _is_settings_page_visible(self) -> bool:
        """通过设置页定位器判断是否已进入设备设置页面"""
        return (
            self._is_element_present(*SettingsLocators.RL_WORK_MODE)
            or self._is_element_present(*SettingsLocators.BTN_REBOOT_DEVICE)
            or self._is_element_present(*SettingsLocators.BTN_DELETE_DEVICE)
        )

    def click_settings_gear(self) -> bool:
        """点击右上角齿轮，并确认已进入设置页面"""
        print("[LivePage] 点击右上角 '设置齿轮' 图标")

        return self.click_and_wait_for(
            click_locator=LiveLocators.BTN_SETTINGS,
            target_condition=self._is_settings_page_visible,
            click_timeout=5,
            page_timeout=8,
            retries=3
        )

    def click_card_playback(self) -> bool:
        """点击底部“卡回放”按钮"""
        print("[LivePage] 点击底部 '卡回放' 按钮")
        return self.safe_click(
            LiveLocators.TV_CARD_PLAYBACK,
            auto_scroll=False,
            retries=3
        )

    def click_cloud_playback(self) -> bool:
        """点击底部“云回放”按钮"""
        print("[LivePage] 点击底部 '云回放' 按钮")
        return self.safe_click(
            LiveLocators.TV_CLOUD_PLAYBACK,
            auto_scroll=False,
            retries=3
        )

    def click_back_to_home(self) -> bool:
        """从 Live 预览页返回 APP 首页"""
        print("[LivePage] 点击 Live 页面左上角返回按钮")
        return self.safe_click(
            LiveLocators.BTN_BACK,
            auto_scroll=False,
            retries=3
        )