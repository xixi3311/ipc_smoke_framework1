# locators/pairing/scan_qr_locator.py
import config

PKG = config.APP_PACKAGE

class ScanQRLocators:
    """扫一扫界面 (UI1)"""
    TITLE = ('id', f'{PKG}:id/tvTitle')              # "扫一扫"
    MANUAL_INPUT = ('id', f'{PKG}:id/tvInputManual') # 手动输入
    ALBUM_ICON = ('id', f'{PKG}:id/qr_picture')      # 右上角相册图标
    SCAN_VIEW = ('id', f'{PKG}:id/scanView')         # 扫描区域（可选）
    QR_FLASH = ('id', f'{PKG}:id/qr_flash')          # 闪光灯按钮（可选）