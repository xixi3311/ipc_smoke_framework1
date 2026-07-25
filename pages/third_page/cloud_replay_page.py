# pages/third_page/cloud_replay_page.py
import time
import config
from pages.base_page import BasePage
from locators.third_page_locator.cloud_replay_locator import CloudReplayLocators


class CloudReplayPage(BasePage):
    """云回看页面类 (UI4 事件列表 / UI5 云视频播放)"""

    def is_on_cloud_list_page(self) -> bool:
        """校验是否处于云回看事件列表界面 (UI4)"""
        return self._is_element_present(*CloudReplayLocators.RECYCLER_EVENT_LIST) or \
               self._is_element_present(*CloudReplayLocators.TV_DATE)

    def click_first_event_item(self) -> bool:
        """点击列表中的第一个云视频事件，跳转至播放页 (UI5)"""
        print("[CloudReplayPage] 点击云视频列表中的第一个事件卡片...")
        if self.safe_click(CloudReplayLocators.FIRST_EVENT_ITEM, auto_scroll=False):
            time.sleep(1.0)
            return True
        return False

    def wait_for_stream_loaded(self, timeout: int = getattr(config, 'PREVIEW_TIMEOUT', 30)) -> bool:
        """【兼容旧接口】判定云回看是否成功出图"""
        success, _ = self.wait_for_stream_loaded_with_time(timeout=timeout)
        return success

    def wait_for_stream_loaded_with_time(self, timeout: int = getattr(config, 'PREVIEW_TIMEOUT', 30)):
        """
        【精准判定云回看出图及耗时】
        :return: (is_success: bool, elapsed_duration: float)
        """
        print(f"[CloudReplayPage] ⏳ 开始检测云视频播放出图状态，最长等待 {timeout} 秒...")
        time.sleep(0.8)
        start_time = time.time()

        while time.time() - start_time < timeout:
            has_controls = self._is_element_present(*CloudReplayLocators.BTN_PLAY_PAUSE) or \
                           self._is_element_present(*CloudReplayLocators.TV_DATE)
            loading_exists = self._is_element_present(*CloudReplayLocators.LOADING_LAYOUT)

            if not loading_exists and has_controls:
                time.sleep(0.5)
                if not self._is_element_present(*CloudReplayLocators.LOADING_LAYOUT):
                    duration = round(time.time() - start_time - 0.5 + 0.8, 2)
                    print(f"[CloudReplayPage] ✅ 云回看视频加载成功！画面已出图，真实耗时: {duration} 秒")
                    return True, duration

            time.sleep(0.3)

        total_duration = round(time.time() - start_time + 0.8, 2)
        print(f"[CloudReplayPage] ❌ 云回看视频加载超时 ({timeout}s)！")
        return False, total_duration

    def click_back_to_live(self) -> bool:
        """从云回看界面点击左上角返回 Live 预览界面"""
        print("[CloudReplayPage] 点击返回按钮退回 Live 界面...")
        return self.safe_click(('id', f'{config.APP_PACKAGE}:id/btnBack'), auto_scroll=False)
















