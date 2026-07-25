# pages/pairing/add_device_page.py
import time
from pages.base_page import BasePage
from locators.pairing_locator.add_device_locator import AddDeviceLocators

class AddDevicePage(BasePage):
    """添加设备页面 (UI3/UI4)"""

    def is_on_add_device_page(self) -> bool:
        return self._is_element_present(*AddDeviceLocators.TITLE)

    def check_hear_alert(self, check=True) -> bool:
        """勾选/取消 '已听到设备播报配网提示音'"""
        self.logger.info(f"设置复选框状态: {check}")
        checkbox = self.driver.xpath(AddDeviceLocators.CHECKBOX[1])  # 或使用id
        # 这里使用id定位
        elem = self.driver(resourceId=AddDeviceLocators.CHECKBOX[1])
        if elem.exists:
            current_checked = elem.info.get("checked", False)
            if current_checked != check:
                elem.click()
                time.sleep(0.3)
            return True
        else:
            # 备用：点击文本区域
            return self.safe_click(AddDeviceLocators.CHECKBOX_TEXT, auto_scroll=False)

    def click_hotspot_pairing(self) -> bool:
        self.logger.info("点击热点配网")
        return self.safe_click(AddDeviceLocators.HOTSPOT_PAIR, auto_scroll=False)

    def click_qr_pairing(self) -> bool:
        self.logger.info("点击二维码配网")
        return self.safe_click(AddDeviceLocators.QR_PAIR, auto_scroll=False)