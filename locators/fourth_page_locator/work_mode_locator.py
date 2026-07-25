# locators/fourth_page_locator/work_mode_locator.py
import config

PKG = config.APP_PACKAGE

class WorkModeLocators:
    """工作模式选择页面定位器 (UI5)"""

    # 显式添加 PKG 属性，方便 Page 页直接引用 WorkModeLocators.PKG
    PKG = config.APP_PACKAGE

    # 1. 页面标识与返回
    TITLE_WORK_MODE = ('xpath', "//*[@text='工作模式']")
    BTN_BACK = ('xpath', "//android.widget.ImageButton | //*[@resource-id='com.xc.sv360:id/left_img']")

    # 2. 各模式右侧触发切换的 RadioButton (Cb)
    # 模式1: 省电 / 低功耗模式
    CB_LOW_POWER = ('id', f'{PKG}:id/aovWorkMode1Cb')
    # 模式2: 常电模式
    CB_ALWAYS_ON = ('id', f'{PKG}:id/aovWorkMode2Cb')
    # 模式3: AOV 模式
    CB_AOV = ('id', f'{PKG}:id/aovWorkMode3Cb')
    # 模式4: AOR / 定时录像模式
    CB_AOR = ('id', f'{PKG}:id/aovWorkMode4Cb')
    # 模式5: 休眠模式
    CB_SLEEP = ('id', f'{PKG}:id/aovWorkMode5Cb')



