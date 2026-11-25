import time
from pages.base_page import BasePage
from locators.fourth_page_locator.sdcard_storage_locator import SdCardStorageLocators


class SdCardStoragePage(BasePage):
    """SD 卡存储空间页面"""

    # 页面判断与格式化状态
    def is_on_storage_page(self) -> bool:
        return self.wait_until(
            lambda: self._is_element_present(*SdCardStorageLocators.TITLE),
            timeout=5
        )

    def is_format_confirm_dialog_visible(self) -> bool:
        return self._is_element_present(*SdCardStorageLocators.DIALOG_FORMAT_CONFIRM)

    def get_format_status(self) -> str:
        if self._is_element_present(*SdCardStorageLocators.FORMAT_SUCCESS_TITLE):
            return "success"
        if self._is_element_present(*SdCardStorageLocators.FORMAT_FAILED_TITLE):
            return "failed"
        if self._is_element_present(*SdCardStorageLocators.FORMAT_PROGRESS_TITLE):
            return "formatting"
        return ""

    # 格式化操作
    def click_format(self) -> bool:
        print("[SdCardStoragePage] 点击格式化")
        return self.safe_click(SdCardStorageLocators.BTN_FORMAT, auto_scroll=False)

    def confirm_format(self) -> bool:
        print("[SdCardStoragePage] 确认格式化")
        return self.safe_click(SdCardStorageLocators.BTN_DIALOG_CONFIRM, auto_scroll=False)

    def wait_for_format_result(self, timeout: int = 90) -> str:
        print(f"[SdCardStoragePage] 等待格式化结果，最长 {timeout} 秒")
        end_time = time.time() + timeout

        while time.time() < end_time:
            status = self.get_format_status()
            if status in ("success", "failed"):
                print(f"[SdCardStoragePage] 格式化结果: {status}")
                return status
            time.sleep(0.5)

        print(f"[SdCardStoragePage] 格式化等待超时 ({timeout} 秒)")
        return "timeout"

    def click_format_failed_cancel(self) -> bool:
        print("[SdCardStoragePage] 格式化失败，点击取消")
        return self.safe_click(
            SdCardStorageLocators.BTN_FORMAT_FAILED_CANCEL,
            auto_scroll=False
        )

    def click_format_success_confirm(self) -> bool:
        print("[SdCardStoragePage] 格式化完成，点击知道了")
        return self.safe_click(
            SdCardStorageLocators.BTN_FORMAT_SUCCESS_CONFIRM,
            auto_scroll=False
        )

    def click_format_confirm_cancel(self) -> bool:
        print("[SdCardStoragePage] 取消格式化")
        return self.safe_click(
            SdCardStorageLocators.BTN_DIALOG_CANCEL,
            auto_scroll=False
        )