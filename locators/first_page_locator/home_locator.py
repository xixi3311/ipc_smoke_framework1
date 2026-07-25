# locators/first_page_locator/home_locator.py
import config

PKG = config.APP_PACKAGE


class HomeLocators:
    """
    首页特定标识与卡片控件定位器
    """
    # ---------------- 静态顶层控件 ----------------
    Home_TOP_PLUS_BTN = ('id', f'{PKG}:id/addDeviceBtn')
    HOME_TAB_LAYOUT = ('id', f'{PKG}:id/tab_layout')

    # 弹出菜单子选项
    MENU_ADD_DEVICE = ('xpath', f"//*[@resource-id='{PKG}:id/popMenuText' and @text='添加设备']")
    MENU_SCAN_QR = ('xpath', f"//*[@resource-id='{PKG}:id/popMenuText' and @text='扫一扫']")
    MORE_MENU_SETTINGS = ('xpath', f"//*[@resource-id='{PKG}:id/text' and @text='设置']")

    # ---------------- 元素集合 ----------------
    ALL_DEVICE_NAMES = ('xpath', f"//*[@resource-id='{PKG}:id/deviceName']")

    @staticmethod
    def _escape_xpath_text(text: str) -> str:
        """安全转义 XPath 文本"""
        if "'" not in text:
            return f"'{text}'"
        if '"' not in text:
            return f'"{text}"'
        parts = text.split("'")
        return "concat(" + ", \"'\", ".join(f"'{p}'" for p in parts) + ")"

    @classmethod
    def get_device_name_locator(cls, device_name: str):
        safe_name = cls._escape_xpath_text(device_name)
        return ('xpath', f"//*[@resource-id='{PKG}:id/deviceName' and @text={safe_name}]")

    @classmethod
    def get_play_btn_by_device_name(cls, device_name: str):
        """顺着设备名字文本节点，精准找紧随其后的第一个播放按钮"""
        safe_name = cls._escape_xpath_text(device_name)
        return ('xpath', f"//*[@resource-id='{PKG}:id/deviceName' and @text={safe_name}]/following::*[@resource-id='{PKG}:id/btnPlay'][1]")

    @classmethod
    def get_more_btn_by_device_name(cls, device_name: str):
        """顺着设备名字文本节点，精准找紧随其后的第一个 '⋮' 更多按钮"""
        safe_name = cls._escape_xpath_text(device_name)
        return ('xpath', f"//*[@resource-id='{PKG}:id/deviceName' and @text={safe_name}]/following::*[@resource-id='{PKG}:id/ivMore'][1]")

    @classmethod
    def get_offline_tv_by_device_name(cls, device_name: str):
        """顺着设备名字文本节点，精准找紧随其后的离线提示文本"""
        safe_name = cls._escape_xpath_text(device_name)
        return ('xpath', f"//*[@resource-id='{PKG}:id/deviceName' and @text={safe_name}]/following::*[@resource-id='{PKG}:id/tvDeviceOffline'][1]")





