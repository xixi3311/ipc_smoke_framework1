# pages/pairing/manual_input_dialog.py
from pages.base_page import BasePage
from locators.pairing_locator.manual_input_locator import ManualInputLocators

class ManualInputDialog(BasePage):
    """手动输入设备ID弹窗"""

    def is_on_dialog(self) -> bool:
        return self._is_element_present(*ManualInputLocators.TITLE)

    def input_device_id(self, sn: str) -> bool:
        self.logger.info(f"输入设备SN: {sn}")
        return self.input_text(ManualInputLocators.EDIT_TEXT, sn)

    def click_confirm(self) -> bool:
        self.logger.info("点击确定")
        return self.safe_click(ManualInputLocators.CONFIRM, auto_scroll=False)

    def click_cancel(self) -> bool:
        self.logger.info("点击取消")
        return self.safe_click(ManualInputLocators.CANCEL, auto_scroll=False)