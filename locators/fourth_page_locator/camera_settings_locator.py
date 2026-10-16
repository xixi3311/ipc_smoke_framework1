import config


PKG = config.APP_PACKAGE


class CameraSettingsLocators:
    """摄像机设置页面定位器"""

    # 页面标识与返回
    TITLE = ('id', f'{PKG}:id/centerText')
    BTN_BACK = ('id', f'{PKG}:id/left_img')

    # 画面翻转入口与当前状态摘要
    ENTRY_IMAGE_FLIP = ('xpath', "//*[@text='画面翻转']")
    TV_IMAGE_FLIP_STATUS = ('id', f'{PKG}:id/imageFlpStatusTV')