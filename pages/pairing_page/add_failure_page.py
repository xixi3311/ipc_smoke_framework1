# pages/pairing/add_failure_page.py
from pages.base_page import BasePage
from locators.pairing_locator.add_failure_locator import AddFailureLocators

class AddFailurePage(BasePage):
    """添加失败界面 (UI10)"""

    def is_on_failure_page(self) -> bool:
        return self._is_element_present(*AddFailureLocators.FAIL_TEXT)

    def click_retry(self) -> bool:
        self.logger.info("点击重试")
        return self.safe_click(AddFailureLocators.RETRY_BTN, auto_scroll=False)

    def click_reason(self) -> bool:
        """点击'常见失败原因?'查看详情"""
        self.logger.info("点击常见失败原因")
        return self.safe_click(AddFailureLocators.REASON, auto_scroll=False)