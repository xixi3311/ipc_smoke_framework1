# pages/pairing/connect_wlan_page.py
from pages.base_page import BasePage
from locators.pairing_locator.connect_wlan_locator import ConnectWlanLocators

class ConnectWlanPage(BasePage):
    """连接设备WLAN界面 (UI6)"""

    def is_on_connect_wlan_page(self) -> bool:
        return self._is_element_present(*ConnectWlanLocators.TITLE)

    def click_connect_wlan(self) -> bool:
        self.logger.info("点击连接设备WLAN")
        return self.safe_click(ConnectWlanLocators.CONNECT_BTN, auto_scroll=False)

    def click_not_found_ap(self) -> bool:
        """点击 '未发现设备热点？' """
        self.logger.info("点击未发现设备热点链接")
        return self.safe_click(ConnectWlanLocators.NOT_FOUND_AP, auto_scroll=False)