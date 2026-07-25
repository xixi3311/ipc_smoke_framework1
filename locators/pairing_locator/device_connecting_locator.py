# locators/pairing/device_connecting_locator.py
import config

PKG = config.APP_PACKAGE

class DeviceConnectingLocators:
    """设备联网中界面 (UI8)"""
    TITLE = ('xpath', "//*[@text='设备联网']")
    PROGRESS_BAR = ('id', f'{PKG}:id/progressBar')
    COUNT_DOWN = ('id', f'{PKG}:id/tvCountDown')          # 倒计时 "5S"
    STATE_TEXT = ('id', f'{PKG}:id/tvDeviceConnectingNetworkState')  # "设备联网中......"
    TIPS = ('id', f'{PKG}:id/tvDeviceConnectingNetworkDes')  # 提示文本
    PAIRING_TIP = ('id', f'{PKG}:id/pairingTipTv')