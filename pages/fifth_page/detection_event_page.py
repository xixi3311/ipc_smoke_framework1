from pages.base_page import BasePage
from locators.fifth_page_locator.detection_event_locator import DetectionEventLocators


class DetectionEventPage(BasePage):
    """侦测事件详情页面"""

    # 页面判断与开关状态
    def is_on_detection_event_page(self) -> bool:
        return self.wait_until(
            lambda: (
                self._is_element_present(
                    *DetectionEventLocators.TITLE
                )
                and self._is_element_present(
                    *DetectionEventLocators.EVENT_SWITCH
                )
            ),
            timeout=5
        )

    def is_detection_enabled(self) -> bool:
        try:
            element = self._get_element(
                DetectionEventLocators.EVENT_SWITCH
            )
            return (
                element.exists
                and element.info.get("checked", False)
            )
        except Exception as e:
            self.logger.warning(
                f"[DetectionEventPage] 读取侦测开关状态失败: {e}"
            )
            return False

    # 页面操作
    def enable_detection(self) -> bool:
        print("[DetectionEventPage] 开启当前侦测事件")

        if self.is_detection_enabled():
            return True

        if not self.safe_click(
            DetectionEventLocators.EVENT_SWITCH,
            auto_scroll=False
        ):
            return False

        return self.wait_until(
            self.is_detection_enabled,
            timeout=5
        )

    def click_back(self) -> bool:
        print("[DetectionEventPage] 返回智能侦测页面")
        return self.safe_click(
            DetectionEventLocators.BTN_BACK,
            auto_scroll=False
        )