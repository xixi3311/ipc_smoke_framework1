# pages/pairing/device_name_page.py
from pages.base_page import BasePage
from locators.pairing_locator.device_name_locator import DeviceNameLocators

class DeviceNamePage(BasePage):

    def is_on_device_name_page(self) -> bool:
        return self._is_element_present(*DeviceNameLocators.TITLE)

    def input_device_name(self, name: str) -> bool:
        self.logger.info(f"输入设备名称: {name}")
        result = self.input_text(DeviceNameLocators.DEVICE_NAME_EDIT, name)
        if result:
            self.hide_keyboard()
        return result

    def click_complete(self) -> bool:
        self.logger.info("点击完成")
        return self.safe_click(DeviceNameLocators.COMPLETE_BTN, auto_scroll=False)

    def click_common_name(self, name: str) -> bool:
        locator = ('xpath', f"//*[@resource-id='{self.driver.app_package}:id/textView' and @text='{name}']")
        return self.safe_click(locator, auto_scroll=False)