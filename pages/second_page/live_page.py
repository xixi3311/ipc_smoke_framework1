# pages/second_page/live_page.py
import time
import config
from pages.base_page import BasePage
from locators.second_page_locator.live_locator import LiveLocators


class LivePage(BasePage):
    """Live 实时预览页面类"""

    def is_on_live_page(self) -> bool:
        """校验当前是否处于 Live 预览页"""
        return self._is_element_present(*LiveLocators.TV_CARD_PLAYBACK) or \
            self._is_element_present(*LiveLocators.BTN_SETTINGS)

    def wait_for_stream_loaded(self, timeout: int = getattr(config, 'PREVIEW_TIMEOUT', 30)) -> bool:
        """
        【兼容旧接口】判定 Live 是否成功出图
        """
        success, _ = self.wait_for_stream_loaded_with_time(timeout=timeout)
        return success

    def wait_for_stream_loaded_with_time(self, timeout: int = getattr(config, 'PREVIEW_TIMEOUT', 30)):
        """
        【精准判定 Live 画面出图及耗时】
        :return: (is_success: bool, elapsed_duration: float)
        """
        print(f"[LivePage] ⏳ 开始检测 Live 画面出图状态，最长等待 {timeout} 秒...")
        start_time = time.time()

        # ---------------- 阶段 1：前置等待转圈(LOADING_LAYOUT)弹起 (最多 2.5 秒) ----------------
        init_deadline = time.time() + 2.5
        while time.time() < init_deadline:
            if self._is_element_present(*LiveLocators.LOADING_LAYOUT):
                break
            time.sleep(0.1)

        # ---------------- 阶段 2：等待转圈消失 & 播放容器就绪 ----------------
        while time.time() - start_time < timeout:
            loading_exists = self._is_element_present(*LiveLocators.LOADING_LAYOUT)
            video_container_present = self._is_element_present(*LiveLocators.VIDEO_CONTAINER)

            if not loading_exists and video_container_present and self.is_on_live_page():
                # 防抖校验：等待 0.5s 确认不是网络波动导致的二次转圈
                time.sleep(0.5)
                if not self._is_element_present(*LiveLocators.LOADING_LAYOUT):
                    # 🎯 准确记录出图时间（扣除防抖 0.5s）
                    duration = round(time.time() - start_time - 0.5, 2)
                    print(f"[LivePage] ✅ Live 画面加载成功！真实出图耗时: {duration} 秒")

                    # 👁️ 额外停留 2 秒供人工目测确认真实画面（不计入出图耗时）
                    print("[LivePage]  停留 2.0 秒以便目测确认出图画面...")
                    time.sleep(2.0)

                    return True, duration

            time.sleep(0.2)

        total_duration = round(time.time() - start_time, 2)
        print(f"[LivePage] ❌ Live 画面加载超时 ({timeout}s)，未能成功出图！")
        return False, total_duration

    def click_settings_gear(self) -> bool:
        """点击右上角齿轮进入设置界面"""
        print("[LivePage] 点击右上角 '设置齿轮' 图标")
        return self.safe_click(LiveLocators.BTN_SETTINGS, auto_scroll=False)

    def click_card_playback(self) -> bool:
        """点击底部 '卡回放' 切换至 SD 卡回看界面"""
        print("[LivePage] 点击底部 '卡回放' 按钮")
        return self.safe_click(LiveLocators.TV_CARD_PLAYBACK, auto_scroll=False)

    def click_cloud_playback(self) -> bool:
        """点击底部 '云回放' 切换至云存回看界面"""
        print("[LivePage] 点击底部 '云回放' 按钮")
        return self.safe_click(LiveLocators.TV_CLOUD_PLAYBACK, auto_scroll=False)

    def click_back_to_home(self) -> bool:
        """从 Live 预览页返回 APP 首页"""
        print("[LivePage] 点击 Live 界面左上角返回按钮回到首页...")
        return self.safe_click(LiveLocators.BTN_BACK, auto_scroll=False)