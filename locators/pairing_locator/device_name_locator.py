# locators/pairing/device_name_locator.py
import config

PKG = config.APP_PACKAGE

class DeviceNameLocators:
    """设备名称设置界面 (UI9)"""
    TITLE = ('xpath', "//*[@text='设备名称']")
    DEVICE_NAME_EDIT = ('id', f'{PKG}:id/etDeviceName')
    CLEAR_BTN = ('id', f'{PKG}:id/btnClearAccount')       # 清空按钮
    COMMON_NAMES = ('id', f'{PKG}:id/recyclerView')       # 常用名称列表
    COMPLETE_BTN = ('id', f'{PKG}:id/setComplete')