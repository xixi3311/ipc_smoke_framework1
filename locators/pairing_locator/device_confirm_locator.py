# locators/pairing/device_confirm_locator.py
import config

PKG = config.APP_PACKAGE


class DeviceConfirmLocators:
    """设备确认页（已添加该设备提示）"""
    TIP_TEXT = f'{PKG}:id/deviceConfirmTipTv'
    KNOW_BTN = f'{PKG}:id/deviceConfirmKnow'