#device_confirm_page.py
import time
import allure
from pages.base_page import BasePage
from locators.pairing_locator.device_confirm_locator import DeviceConfirmLocators


class DeviceConfirmPage(BasePage):
    """设备确认弹窗页（处理'您已添加该设备'）"""

    def is_already_added_page(self) -> bool:
        """判断是否出现'您已添加该设备'提示"""
        return self.driver(resourceId=DeviceConfirmLocators.TIP_TEXT, text="您已添加该设备").exists

    def click_know(self) -> bool:
        """点击'知道了'按钮"""
        with allure.step("点击『知道了』关闭已添加提示"):
            btn = self.driver(resourceId=DeviceConfirmLocators.KNOW_BTN, text="知道了")
            if btn.exists:
                btn.click()
                time.sleep(1.5)
                return True
            return False