import config

PKG = config.APP_PACKAGE


class CloudReplayLocators:
    """
    云回看定位器 (UI4 列表页 & UI5 播放页)
    """
    # ---------------- UI4: 云回看事件列表界面 ----------------
    # 云列表容器 (GridView / RecyclerView)
    RECYCLER_EVENT_LIST = ('id', f'{PKG}:id/recyclerView')

    # 列表中的第一个云视频卡片 (Clickable 的 rootView)
    FIRST_EVENT_ITEM = ('xpath', f"(//*[@resource-id='{PKG}:id/rootView'])[1]")

    # 日期选择控件
    TV_DATE = ('id', f'{PKG}:id/tvDate')

    # ---------------- UI5: 云视频播放界面 ----------------
    # 视频画面渲染节点 (TextureView)
    TEXTURE_VIEW = ('xpath', '//android.view.TextureView')
    RENDER_CONTAINER = ('id', f'{PKG}:id/renderViewContainer')

    # 播放/暂停控制按钮
    BTN_PLAY_PAUSE = ('id', f'{PKG}:id/playBtnBackground')

    # 进度条
    SEEK_BAR = ('id', f'{PKG}:id/seekBar')

    # 底部下载与删除按钮
    TV_DOWNLOAD = ('id', f'{PKG}:id/tvDownload')
    TV_DELETE = ('id', f'{PKG}:id/tvDelete')

    # 左上角返回按键
    BTN_BACK = ('xpath', "//android.widget.ImageButton[@content-desc='Navigate up']")

    # 📌 加载转圈动画 / 提示文本，修复 CloudReplayPage 调取报错问题
    LOADING_LAYOUT = ('xpath',
                      f"//*[contains(@resource-id, '{PKG}:id/loading') or contains(@resource-id, '{PKG}:id/progressBar') or contains(@resource-id, '{PKG}:id/tvLoading')]")