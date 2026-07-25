# locators/second_page_locator/live_locator.py
import config

PKG = config.APP_PACKAGE


class LiveLocators:
    """Live 实时预览页定位器"""

    # 顶部导航 & 设置齿轮
    BTN_BACK = ('id', f'{PKG}:id/btnBack')
    BTN_SETTINGS = ('id', f'{PKG}:id/right_img')  # 右上角齿轮图标
    TV_DEVICE_TITLE = ('id', f'{PKG}:id/tvTitle')

    # 多镜头画面与加载提示
    # 单目/多目渲染容器
    VIDEO_CONTAINER = ('xpath',
                       f"//*[contains(@resource-id, '{PKG}:id/player') or contains(@resource-id, '{PKG}:id/video')]")
    # 加载转圈动画/提示文本
    LOADING_LAYOUT = ('xpath',
                      f"//*[contains(@resource-id, '{PKG}:id/loading') or contains(@resource-id, '{PKG}:id/progressBar') or contains(@resource-id, '{PKG}:id/tvLoading') or contains(@resource-id, '{PKG}:id/videoProgress')]")

    # 底部导航按键 (云回放 / 卡回放 / 报警消息)
    TV_CLOUD_PLAYBACK = ('id', f'{PKG}:id/tvCloudPlayback')
    TV_CARD_PLAYBACK = ('id', f'{PKG}:id/tvCardPlayback')
    TV_ALERT_MESSAGE = ('id', f'{PKG}:id/tvAlertMessage')