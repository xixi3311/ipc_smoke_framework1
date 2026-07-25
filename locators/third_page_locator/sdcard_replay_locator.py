# locators/third_page_locator/sdcard_replay_locator.py
import config

PKG = config.APP_PACKAGE


class SdCardReplayLocators:
    """卡回看界面定位器 (ui2/ui3)"""

    # 返回按钮
    BTN_BACK = ('id', f'{PKG}:id/btnBack')

    # 界面特征元素 (时间轴刻度尺 / 事件列表)
    TIME_RULER = ('id', f'{PKG}:id/time_ruler')
    PLAY_TIME_RV = ('id', f'{PKG}:id/playTimeRv')
    BTN_ZOOM_IN = ('id', f'{PKG}:id/btnZoomIn')
    BTN_ZOOM_OUT = ('id', f'{PKG}:id/btnZoomOut')

    # 加载转圈动画/提示
    LOADING_LAYOUT = ('xpath',
                      f"//*[contains(@resource-id, '{PKG}:id/loading') or contains(@resource-id, '{PKG}:id/progressBar')]")