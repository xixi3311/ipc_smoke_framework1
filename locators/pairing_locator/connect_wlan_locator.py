# locators/pairing/connect_wlan_locator.py
import config

PKG = config.APP_PACKAGE

class ConnectWlanLocators:
    """连接设备WLAN界面 (UI6)"""
    TITLE = ('xpath', "//*[@text='连接设备WLAN']")
    CONNECT_BTN = ('id', f'{PKG}:id/btnStartPairing')
    NOT_FOUND_AP = ('id', f'{PKG}:id/tvNotFoundDeviceAp')  # "未发现设备热点？"
    HELP_TEXT = ('id', f'{PKG}:id/tvConnectDeviceApHelper')