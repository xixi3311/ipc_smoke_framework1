# sdcard_storage_locator.py
import config

PKG = config.APP_PACKAGE


class SdCardStorageLocators:
    """SD 卡存储空间页面定位器"""

    # 页面标识与容量信息
    TITLE = ('xpath', "//*[@text='存储空间']")
    TOTAL_CAPACITY = ('id', f'{PKG}:id/spaceTotal')
    AVAILABLE_CAPACITY = ('id', f'{PKG}:id/spaceAvailable')

    # 格式化入口与确认弹窗
    BTN_FORMAT = ('id', f'{PKG}:id/tvFormat')
    DIALOG_FORMAT_CONFIRM = ('xpath', f"//*[@resource-id='{PKG}:id/tvTitle' and @text='确认格式化？']")
    BTN_DIALOG_CANCEL = ('id', f'{PKG}:id/tvLeft')
    BTN_DIALOG_CONFIRM = ('id', f'{PKG}:id/tvRight')

    # 格式化进度、失败和成功状态
    FORMAT_PROGRESS_TITLE = ('id', f'{PKG}:id/dialogProgressTitle')
    FORMAT_FAILED_TITLE = ('xpath', f"//*[@resource-id='{PKG}:id/tipsTv' and @text='格式化失败']")
    BTN_FORMAT_FAILED_CANCEL = ('id', f'{PKG}:id/popCancleTv')
    FORMAT_SUCCESS_TITLE = ('xpath', f"//*[@resource-id='{PKG}:id/tipsTv' and @text='格式化完成']")
    BTN_FORMAT_SUCCESS_CONFIRM = ('id', f'{PKG}:id/popSubmitTv')