# locators/pairing/add_device_locator.py
import config

PKG = config.APP_PACKAGE

class AddDeviceLocators:
    """添加设备页面 (UI3/UI4)"""
    # 页面标题
    TITLE = ('xpath', "//*[@text='添加设备']")

    # 复选框（已听到配网提示音）
    CHECKBOX = ('id', f'{PKG}:id/checkbox')
    CHECKBOX_TEXT = ('id', f'{PKG}:id/tvHearPairAlert')

    # 配网按钮
    HOTSPOT_PAIR = ('id', f'{PKG}:id/btnPairedByAP')       # 热点配网
    QR_PAIR = ('id', f'{PKG}:id/btnPairedByQrCode')        # 二维码配网

    # 提示文本（可选）
    TIPS1 = ('id', f'{PKG}:id/tvResetTips1')
    TIPS2 = ('id', f'{PKG}:id/tvResetTips2')