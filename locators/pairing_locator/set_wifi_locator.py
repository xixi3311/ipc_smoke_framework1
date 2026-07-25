# locators/pairing/set_wifi_locator.py
import config

PKG = config.APP_PACKAGE

class SetWifiLocators:
    """设置Wi-Fi界面 (UI5)"""
    TITLE = ('xpath', "//*[@text='设置Wi-Fi']")
    WIFI_NAME_EDIT = ('id', f'{PKG}:id/etWifiName')
    WIFI_PASSWORD_EDIT = ('id', f'{PKG}:id/etWifiPassword')
    NEXT_BTN = ('id', f'{PKG}:id/btnStartPairing')
    WIFI_SWITCH_ICON = ('id', f'{PKG}:id/ivSwitchWifi')   # 切换WiFi列表（可选）
    PASSWORD_SHOW = ('id', f'{PKG}:id/btnPasswordShow')    # 显示密码