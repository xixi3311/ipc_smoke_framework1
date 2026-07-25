# pages/pairing/set_wifi_page.py
from pages.base_page import BasePage
from locators.pairing_locator.set_wifi_locator import SetWifiLocators

class SetWifiPage(BasePage):

    def is_on_set_wifi_page(self) -> bool:
        return self._is_element_present(*SetWifiLocators.TITLE)

    def input_wifi_ssid(self, ssid: str) -> bool:
        self.logger.info(f"输入WiFi名称: {ssid}")
        return self.input_text(SetWifiLocators.WIFI_NAME_EDIT, ssid)

    def input_wifi_password(self, password: str) -> bool:
        self.logger.info("输入WiFi密码")
        return self.input_text(SetWifiLocators.WIFI_PASSWORD_EDIT, password)

    def click_next(self) -> bool:
        self.logger.info("点击下一步")
        # 先隐藏键盘，防止按钮被遮挡
        self.hide_keyboard()
        # 再点击下一步按钮
        return self.safe_click(SetWifiLocators.NEXT_BTN, auto_scroll=False)