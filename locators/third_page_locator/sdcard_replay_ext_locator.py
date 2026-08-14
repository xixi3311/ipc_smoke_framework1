# locators/third_page_locator/sdcard_replay_ext_locator.py
import config

PKG = config.APP_PACKAGE


class SdCardReplayExtLocators:
    """卡回看扩展定位器（UI1 ~ UI6）"""

    """注意: LOADING_LAYOUT = 
    ('xpath', "//*[contains(@resource-id, 'com.xc.sv360:id/loading') 
    or contains(@resource-id, 'com.xc.sv360:id/progressBar')]")  #类行属性
    在sdcard_replay_ext_page.py中实现了                              """

    # UI1: 无录像提示
    TV_CENTER_NO_VIDEO = ('id', f'{PKG}:id/tvCenter')          # "未查询到录像"
    CLOUD_GUIDE = ('id', f'{PKG}:id/cloudGuide')               # 云存引导区域

    # UI2: 有录像主界面
    TIME_RULER = ('id', f'{PKG}:id/time_ruler')                  # 时间轴
    PLAY_TIME_RV = ('id', f'{PKG}:id/playTimeRv')               # 事件列表 RecyclerView
    CURRENT_TIME_TV = ('id', f'{PKG}:id/current_time_tv')       # 底部当前播放时间（HH:MM:SS）
    SHOW_DATE_SELECT = ('id', f'{PKG}:id/showDataSelect')     # 日期选择文本（MM-DD）
    IV_VIDEO_TYPE_FILTER = ('id', f'{PKG}:id/ivVideoTypeFilter')        # 事件类型筛选文本

    # UI3: 事件类型选择面板
    EVENT_TYPE_RECYCLER = ('id', f'{PKG}:id/recyclerView')            # 类型列表（在 UI3 中）
    EVENT_TYPE_ITEM = ('xpath', f"//*[@resource-id='{PKG}:id/recyclerView']/*")
    EVENT_TYPE_TEXT = ('id', f'{PKG}:id/tvEventType')          # 类型名称
    EVENT_TYPE_CHECKED = ('id', f'{PKG}:id/ivChecked')         # 选中图标

    # UI4: 日历选择器
    CALENDAR_CONTAINER = ('id', f'{PKG}:id/calendarViewContainer')
    CALENDAR_VIEW = ('id', f'{PKG}:id/calendarView')
    TV_CURRENT_MON = ('id', f'{PKG}:id/tvCurrentMon')          # 当前年月 "2026-8"
    VP_MONTH = ('id', f'{PKG}:id/vp_month')                  # 日期网格 ViewPager

    # ---------------- 事件列表项 (UI2/UI5/UI6) ----------------
    EVENT_ROOT_VIEW = ('id', f'{PKG}:id/rootViews')            # 注意是复数
    # 事件时间文本
    EVENT_TIME_TEXT = ('id', f'{PKG}:id/timeItemTime')
    # 事件类型文本
    EVENT_TYPE_TEXT_ITEM = ('id', f'{PKG}:id/timeItemEvent')   # "有人出现"