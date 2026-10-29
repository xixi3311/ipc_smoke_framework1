import config

PKG = config.APP_PACKAGE


class DetectionLocators:
    """智能侦测页面定位器"""

    # 页面标识与返回
    TITLE = ('xpath', "//*[@text='智能侦测']")
    BTN_BACK = ('xpath', "//android.widget.ImageButton[@content-desc='Navigate up']")

    # 侦测事件状态与入口
    PERSON_STATE = ('xpath', f"//*[@resource-id='{PKG}:id/eventRoot'][.//*[@text='有人出现']]//*[@resource-id='{PKG}:id/eventStateTv']")
    CAR_STATE = ('xpath', f"//*[@resource-id='{PKG}:id/eventRoot'][.//*[@text='有车出现']]//*[@resource-id='{PKG}:id/eventStateTv']")
    CAR_EVENT = ('xpath', f"//*[@resource-id='{PKG}:id/eventRoot'][.//*[@text='有车出现']]")