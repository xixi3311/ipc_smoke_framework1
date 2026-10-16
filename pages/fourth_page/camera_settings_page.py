from pages.base_page import BasePage
from locators.fourth_page_locator.camera_settings_locator import CameraSettingsLocators


class CameraSettingsPage(BasePage):
    """摄像机设置页面"""

    # 页面判断
    def is_on_camera_settings_page(self) -> bool:
        return self.wait_until(
            lambda: (
                self._is_element_present(
                    *CameraSettingsLocators.TITLE
                )
                and self._is_element_present(
                    *CameraSettingsLocators.ENTRY_IMAGE_FLIP
                )
            ),
            timeout=5
        )

    # 状态读取
    def is_image_flip_status_unflipped(self) -> bool:
        try:
            element = self._get_element(
                CameraSettingsLocators.TV_IMAGE_FLIP_STATUS
            )
            return (
                element.exists
                and element.info.get("text", "").strip() == "未翻转"
            )
        except Exception as e:
            self.logger.warning(
                f"[CameraSettingsPage] 读取画面翻转摘要失败: {e}"
            )
            return False

    # 页面操作
    def click_image_flip_entry(self) -> bool:
        print("[CameraSettingsPage] 点击画面翻转入口")
        return self.safe_click(
            CameraSettingsLocators.ENTRY_IMAGE_FLIP,
            auto_scroll=False
        )

    def click_back(self) -> bool:
        print("[CameraSettingsPage] 返回设备设置页")
        return self.safe_click(
            CameraSettingsLocators.BTN_BACK,
            auto_scroll=False
        )