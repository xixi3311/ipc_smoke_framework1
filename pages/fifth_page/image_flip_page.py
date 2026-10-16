from pages.base_page import BasePage
from locators.fifth_page_locator.image_flip_locator import ImageFlipLocators


class ImageFlipPage(BasePage):
    """画面翻转页面"""

    # 页面判断
    def is_on_image_flip_page(self) -> bool:
        return self.wait_until(
            lambda: self._is_element_present(
                *ImageFlipLocators.TITLE
            ),
            timeout=5
        )

    # 选项状态读取
    def is_flipped_selected(self) -> bool:
        try:
            element = self._get_element(
                ImageFlipLocators.CHECKBOX_FLIPPED
            )
            return (
                element.exists
                and element.info.get("checked", False)
            )
        except Exception as e:
            self.logger.warning(
                f"[ImageFlipPage] 读取画面翻转状态失败: {e}"
            )
            return False

    def is_unflipped_selected(self) -> bool:
        try:
            element = self._get_element(
                ImageFlipLocators.CHECKBOX_UNFLIPPED
            )
            return (
                element.exists
                and element.info.get("checked", False)
            )
        except Exception as e:
            self.logger.warning(
                f"[ImageFlipPage] 读取画面不翻转状态失败: {e}"
            )
            return False

    # 页面操作
    def select_flipped(self) -> bool:
        print("[ImageFlipPage] 选择画面翻转")

        if self.is_flipped_selected():
            return True

        if not self.safe_click(
            ImageFlipLocators.OPTION_FLIPPED,
            auto_scroll=False
        ):
            return False

        return self.wait_until(
            self.is_flipped_selected,
            timeout=5
        )

    def click_back(self) -> bool:
        print("[ImageFlipPage] 返回摄像机设置页")
        return self.safe_click(
            ImageFlipLocators.BTN_BACK,
            auto_scroll=False
        )