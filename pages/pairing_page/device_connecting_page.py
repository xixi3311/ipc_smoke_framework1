# pages/pairing_page/device_connecting_page.py
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
        等待配网结果，同时检测以下状态：
        - 出现"您已添加该设备"弹窗 → 返回 (True, "already_added")
        - 进入设备名称设置页 (UI9) → 配网成功
        - 进入添加失败页 (UI10) → 配网失败
        - 一直在联网中 (UI8) → 持续等待直到超时
        :return: (success: bool, error_msg: str)
        """
        self.logger.info(f"等待配网结果，最长 {timeout} 秒...")
        start = time.time()

        from pages.pairing_page.device_name_page import DeviceNamePage
        from pages.pairing_page.add_failure_page import AddFailurePage
        from pages.pairing_page.device_confirm_page import DeviceConfirmPage

        device_name_page = DeviceNamePage(self.driver)
        failure_page = AddFailurePage(self.driver)
        confirm_page = DeviceConfirmPage(self.driver)

        while time.time() - start < timeout:
            # ✅ 1. 最高优先级：已添加弹窗（可能遮挡联网页，必须先判）
            if confirm_page.is_already_added_page():
                self.logger.info("检测到『您已添加该设备』弹窗")
                return True, "already_added"

            # 2. UI9 设备名称设置页 → 成功
            if device_name_page.is_on_device_name_page():
                self.logger.info("配网成功，已进入设备名称设置页 (UI9)")
                return True, ""

            # 3. UI10 添加失败页 → 失败
            if failure_page.is_on_failure_page():
                self.logger.warning("配网失败，进入添加失败页 (UI10)")
                return False, "添加失败"

            # 4. 仍在联网中 (UI8) → 继续等
            if self._is_element_present(*DeviceConnectingLocators.TITLE):
                self.logger.debug("仍在设备联网中页面 (UI8)，继续等待...")
                time.sleep(0.5)
                continue

            # 5. 页面切换间隙
            time.sleep(0.3)

        return False, "配网超时"