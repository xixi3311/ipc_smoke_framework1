from pages.base_page import BasePage
from locators.fourth_page_locator.detection_locator import DetectionLocators


class DetectionPage(BasePage):
    """智能侦测事件列表页"""

    # 页面判断与状态读取
    def is_on_detection_page(self) -> bool:
        return self.wait_until(
            lambda: self._is_element_present(
                *DetectionLocators.TITLE
            ),
            timeout=5
        )

    def _get_event_state(self, locator, event_name: str):
        try:
            element = self._get_element(locator)

            if not element.exists:
                return None

            return element.info.get("text", "").strip()
        except Exception as e:
            self.logger.warning(
                f"[DetectionPage] 读取 {event_name} 状态失败: {e}"
            )
            return None

    def is_person_detection_enabled(self) -> bool:
        return self._get_event_state(
            DetectionLocators.PERSON_STATE,
            "有人出现"
        ) == "已开启"

    def is_car_detection_disabled(self) -> bool:
        return self._get_event_state(
            DetectionLocators.CAR_STATE,
            "有车出现"
        ) == "未开启"

    # 页面操作
    def click_car_event(self) -> bool:
        print("[DetectionPage] 点击有车出现事件")
        return self.safe_click(
            DetectionLocators.CAR_EVENT,
            auto_scroll=False
        )

    def click_back(self) -> bool:
        print("[DetectionPage] 返回设备设置页")
        return self.safe_click(
            DetectionLocators.BTN_BACK,
            auto_scroll=False
        )