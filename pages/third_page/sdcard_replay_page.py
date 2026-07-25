# pages/third_page/sdcard_replay_page.py
import time
import config
from pages.base_page import BasePage
from locators.third_page_locator.sdcard_replay_locator import SdCardReplayLocators


class SdCardReplayPage(BasePage):
    """卡回看页面类 (UI2/UI3)"""

    def is_on_sdcard_replay_page(self) -> bool:
        """根据时间轴和放大缩小按钮判断是否进入卡回看界面"""
        return self._is_element_present(*SdCardReplayLocators.TIME_RULER) or \
            self._is_element_present(*SdCardReplayLocators.BTN_ZOOM_IN)

    def wait_for_stream_loaded(self, timeout: int = getattr(config, 'PREVIEW_TIMEOUT', 30)) -> bool:
        """【兼容旧接口】判定卡回看是否成功出图"""
        success, _ = self.wait_for_stream_loaded_with_time(timeout=timeout)
        return success

    def wait_for_stream_loaded_with_time(self, timeout: int = getattr(config, 'PREVIEW_TIMEOUT', 30)):
        """
        【精准判定 SD 卡回看出图及耗时】
        :return: (is_success: bool, elapsed_duration: float)
        """
        print(f"[SdCardReplay] ⏳ 开始检测【卡回看】画面出图状态，最长等待 {timeout} 秒...")

        # 前置 0.8 秒缓冲
        time.sleep(0.8)
        start_time = time.time()

        while time.time() - start_time < timeout:
            loading_exists = self._is_element_present(*SdCardReplayLocators.LOADING_LAYOUT)

            if not loading_exists and self.is_on_sdcard_replay_page():
                time.sleep(0.5)
                if not self._is_element_present(*SdCardReplayLocators.LOADING_LAYOUT):
                    duration = round(time.time() - start_time - 0.5 + 0.8, 2)
                    print(f"[SdCardReplay] ✅ 卡回看视频加载成功！画面已出图，真实耗时: {duration} 秒")
                    return True, duration

            time.sleep(0.3)

        total_duration = round(time.time() - start_time + 0.8, 2)
        print(f"[SdCardReplay] ❌ 卡回看视频加载超时 ({timeout}s)，未成功出图！")
        return False, total_duration

    def click_back_to_live(self) -> bool:
        """从卡回看页退回 Live 页"""
        print("[SdCardReplay] 点击返回按钮退回 Live 界面...")
        return self.safe_click(SdCardReplayLocators.BTN_BACK, auto_scroll=False)