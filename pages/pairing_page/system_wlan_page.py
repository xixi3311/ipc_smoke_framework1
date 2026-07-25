# pages/pairing/system_wlan_page.py
import time
from pages.base_page import BasePage
from locators.pairing_locator.system_wlan_locator import (SystemWlanLocators)

class SystemWlanPage(BasePage):
    """系统WLAN界面 (UI7)"""

    def is_on_system_wlan_page(self) -> bool:
        return self._is_element_present(*SystemWlanLocators.TITLE_WLAN)

    def _find_and_click_ssid(self, ssid: str) -> bool:
        """内部方法：在当前屏幕查找SSID并点击"""
        locator = SystemWlanLocators.get_ssid_item_locator(ssid)
        if self._is_element_present(*locator):
            self.logger.info(f"在当前屏幕找到 {ssid}")
            return self.safe_click(locator, auto_scroll=False)
        return False

    def connect_to_device_hotspot(self, sn: str, max_retries=3) -> bool:
        """
        在系统WLAN列表中连接设备热点（SV-{sn}）
        :param sn: 设备序列号
        """
        target_ssid = f"SV-{sn}"
        self.logger.info(f"开始查找并连接热点: {target_ssid}")

        # 等待列表加载
        time.sleep(2)

        # 首次尝试查找
        for attempt in range(max_retries):
            # 1. 检查当前屏幕
            if self._find_and_click_ssid(target_ssid):
                self.logger.info(f"成功点击热点 {target_ssid}")
                time.sleep(5)  # 等待连接
                return True

            # 2. 下拉刷新（模拟从顶部下拉）
            self.logger.info(f"第 {attempt+1} 次尝试：执行下拉刷新")
            # 注意：系统WLAN页面顶部有开关，下拉可能触发刷新
            self.driver.swipe_ext("up", scale=0.8)  # 轻微上滑模拟下拉
            time.sleep(1.5)
            if self._find_and_click_ssid(target_ssid):
                return True

            # 3. 向下滑动搜索（多次）
            for i in range(5):
                self.logger.info(f"向下滑动搜索，第 {i+1} 次")
                self.driver.swipe_ext("up", scale=0.8)
                time.sleep(0.8)
                if self._find_and_click_ssid(target_ssid):
                    return True

            # 4. 滑到顶部再试
            self.logger.info("滑动到底未找到，滑到顶部")
            for _ in range(5):
                self.driver.swipe_ext("down", scale=1.8)
                time.sleep(0.5)
            # 再执行一次下拉刷新
            self.driver.swipe_ext("up", scale=0.8)
            time.sleep(1.5)

        self.logger.error(f"经过 {max_retries} 轮尝试仍未找到热点 {target_ssid}")
        return False