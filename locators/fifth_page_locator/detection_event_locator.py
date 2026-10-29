import config


PKG = config.APP_PACKAGE


class DetectionEventLocators:
    """侦测事件详情页面定位器"""

    # 页面标识与返回
    TITLE = ('id', f'{PKG}:id/centerText')
    BTN_BACK = ('id', f'{PKG}:id/left_img')

    # 当前事件及其开关
    EVENT_NAME = ('id', f'{PKG}:id/intelligentCamera1type')
    EVENT_SWITCH = ('id', f'{PKG}:id/intelligentCamera1Sth')