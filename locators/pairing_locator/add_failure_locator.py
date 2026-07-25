# locators/pairing/add_failure_locator.py
import config

PKG = config.APP_PACKAGE

class AddFailureLocators:
    """添加失败界面 (UI10)"""
    TITLE = ('xpath', "//*[@text='添加设备']")   # 顶部标题仍然为"添加设备"
    FAIL_ICON = ('id', f'{PKG}:id/ivPairFailure')
    FAIL_TEXT = ('id', f'{PKG}:id/tvPairFailure')       # "添加失败"
    REASON = ('id', f'{PKG}:id/tvPairFailureReason')    # "常见失败原因?"
    RETRY_BTN = ('id', f'{PKG}:id/btnRetry')