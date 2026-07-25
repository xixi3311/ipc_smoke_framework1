import config

PKG = config.APP_PACKAGE


class SettingsLocators:
    """设备设置页面定位器 (UI1 ~ UI5)"""

    # ---------------- UI1: 设置页面顶部标志位 & 工作模式入口 ----------------
    # 设置页标题
    TV_TITLE = ('id', f'{PKG}:id/tvTitle')

    # 工作模式整行入口
    RL_WORK_MODE = ('id', f'{PKG}:id/aovWorkModeRel')
    # 当前工作模式显示的文本
    TV_WORK_MODE_VAL = ('id', f'{PKG}:id/aovWorkModeTv')

    # ---------------- UI2: 设置页面底部按钮 ----------------
    # 重启设备按钮
    BTN_REBOOT_DEVICE = ('id', f'{PKG}:id/rebootDevice')

    # 删除设备按钮
    BTN_DELETE_DEVICE = ('id', f'{PKG}:id/deleteDevice')

    # ---------------- UI3 & UI4: 二次确认弹窗控件 ----------------
    # 弹窗提示文本 ("是否重启设备？" 或 "确定删除设备吗？")
    TV_DIALOG_CONTENT = ('id', f'{PKG}:id/tvContent')

    # 弹窗按钮
    BTN_DIALOG_CANCEL = ('id', f'{PKG}:id/tvLeft')   # 取消
    BTN_DIALOG_CONFIRM = ('id', f'{PKG}:id/tvRight')  # 确定

    # ---------------- UI5: 工作模式切换页面 ----------------
    # 各工作模式面板/选项
    MODE_LOW_POWER = ('id', f'{PKG}:id/aovWorkMode1')     # 低功耗模式
    MODE_CONTINUOUS = ('id', f'{PKG}:id/aovWorkMode2')    # 持续录像/微功耗
    MODE_SLEEP = ('id', f'{PKG}:id/aovWorkMode5Tv')       # 休眠模式

    # 工作模式页顶部的返回按键
    BTN_BACK = ('xpath', "//android.widget.ImageButton | //*[@resource-id='com.xc.sv360:id/left_img']")












