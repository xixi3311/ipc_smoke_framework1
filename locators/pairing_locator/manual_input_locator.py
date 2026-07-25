# locators/pairing/manual_input_locator.py
import config

PKG = config.APP_PACKAGE

class ManualInputLocators:
    """手动输入设备ID弹窗 (UI2)"""
    TITLE = ('id', f'{PKG}:id/title')                # "请输入设备ID"
    EDIT_TEXT = ('id', f'{PKG}:id/tv_edit')          # 输入框
    CANCEL = ('id', f'{PKG}:id/tv_cancel')
    CONFIRM = ('id', f'{PKG}:id/tv_confirm')