# pages/pairing/scan_qr_page.py
from pages.base_page import BasePage
from locators.pairing_locator.scan_qr_locator import ScanQRLocators

class ScanQRPage(BasePage):
    """扫一扫页面"""

    def is_on_scan_qr_page(self) -> bool:
        return self._is_element_present(*ScanQRLocators.TITLE)

    def click_manual_input(self) -> bool:
        self.logger.info("点击手动输入")
        return self.safe_click(ScanQRLocators.MANUAL_INPUT, auto_scroll=False)

    def click_album_icon(self) -> bool:
        """点击右上角相册图标（二维码配网用）"""
        self.logger.info("点击相册图标")
        return self.safe_click(ScanQRLocators.ALBUM_ICON, auto_scroll=False)