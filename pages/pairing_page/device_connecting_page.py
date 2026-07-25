# pages/pairing/device_connecting_page.py
import time
from pages.base_page import BasePage
from locators.pairing_locator.device_connecting_locator import DeviceConnectingLocators

class DeviceConnectingPage(BasePage):
    """设备联网中界面 (UI8)"""

    def is_on_connecting_page(self, timeout=10) -> bool:
        """等待页面出现"""
        start = time.time()
        while time.time() - start < timeout:
            if self._is_element_present(*DeviceConnectingLocators.TITLE):
                return True
            time.sleep(0.5)
        return False

    def wait_for_result(self, timeout=180) -> tuple:
        """
        等待配网结果
        :return: (success: bool, error_msg: str)
        """
        self.logger.info(f"等待配网结果，最长 {timeout} 秒...")
        start = time.time()
        # 轮询检测是否进入成功页面（设备名称）或失败页面
        from pages.pairing_page.device_name_page import DeviceNamePage
        from pages.pairing_page.add_failure_page import AddFailurePage
        device_name_page = DeviceNamePage(self.driver)
        failure_page = AddFailurePage(self.driver)

        while time.time() - start < timeout:
            if device_name_page.is_on_device_name_page():
                self.logger.info("配网成功，进入设备名称设置页")
                return True, ""
            if failure_page.is_on_failure_page():
                self.logger.warning("配网失败，进入添加失败页")
                return False, "添加失败"
            # 检查是否仍在联网中页面
            if not self.is_on_connecting_page(timeout=2):
                self.logger.warning("页面跳转异常，可能已经退出联网页")
            time.sleep(1)

        return False, "配网超时"