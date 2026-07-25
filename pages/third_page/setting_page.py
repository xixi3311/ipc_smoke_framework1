import time
from pages.base_page import BasePage
from locators.third_page_locator.setting_locator import SettingsLocators
from pages.fourth_page.work_mode_page import WorkModePage


class SettingsPage(BasePage):
    """设备设置页面类 """

    def is_on_settings_page(self) -> bool:
        """校验当前是否处于设备设置界面 """
        print("[SettingsPage] 正在校验是否进入【设备设置】界面...")
        start_time = time.time()
        while time.time() - start_time < 3:
            if self._is_element_present(*SettingsLocators.TV_TITLE) or \
               self._is_element_present(*SettingsLocators.RL_WORK_MODE):
                return True
            time.sleep(0.5)
        return False

    # ================= UI1 & UI5: 工作模式相关操作 =================
    def click_work_mode_entry(self) -> bool:
        """点击『工作模式』整行进入选择界面 (UI5)"""
        print("[SettingsPage] 点击『工作模式』入口...")
        return self.safe_click(SettingsLocators.RL_WORK_MODE, auto_scroll=False)

    def is_on_work_mode_page(self) -> bool:
        """校验是否已进入【工作模式选择】界面 """
        print("[SettingsPage] 校验是否处于【工作模式】界面...")
        return self._is_element_present(*SettingsLocators.MODE_SLEEP) or \
               self._is_element_present(*SettingsLocators.MODE_LOW_POWER)

    # ================= UI2 & UI3: 重启设备相关操作 =================
    def click_reboot_device(self) -> bool:
        """在设置页底端点击『重启设备』按钮 """
        print("[SettingsPage] 正在滑动寻找并点击『重启设备』按钮...")

        # 1. 优先尝试通过 ID 滑动寻找并点击
        if self.safe_click(SettingsLocators.BTN_REBOOT_DEVICE, auto_scroll=True):
            print("[SettingsPage] ✅ 通过 ID 成功找到并点击『重启设备』")
            return True

        # 2. 备用方案：如果通过 ID 未找到，使用 XPath 匹配文本 "重启设备" 滑动寻找
        print("[SettingsPage] ⚠️ 通过 ID 未找到，尝试通过文本 '重启设备' 寻找...")
        text_reboot_locator = ('xpath', "//*[@text='重启设备']")
        if self.safe_click(text_reboot_locator, auto_scroll=True):
            print("[SettingsPage] ✅ 通过文本成功找到并点击『重启设备』")
            return True

        # 3. 两种方式都未找到，明确返回 False，防止返回 None
        print("[SettingsPage] ❌ 无法在页面找到『重启设备』按钮")
        return False

    def confirm_reboot_dialog(self) -> bool:
        """重启弹窗弹出后，点击『确定』按键 """
        print("[SettingsPage] 正在确认重启弹窗，点击『确定』...")
        if self._is_element_present(*SettingsLocators.BTN_DIALOG_CONFIRM):
            self.safe_click(SettingsLocators.BTN_DIALOG_CONFIRM, auto_scroll=False)
            time.sleep(1.0)
            return True
        print("[SettingsPage] ❌ 未检测到重启确认弹窗！")
        return False

    # ================= UI2 & UI4: 删除设备逻辑 =================
    def click_delete_device(self) -> bool:
        """在设置页最底端滑动并点击『删除设备』按钮 """
        print("[SettingsPage] 正在滑动寻找并点击『删除设备』按钮...")
        return self.safe_click(SettingsLocators.BTN_DELETE_DEVICE, auto_scroll=True)

    def confirm_delete_dialog(self, confirm: bool = False) -> bool:
        """
        处理删除设备弹窗
        :param confirm: True 点击『确定』删除，False 点击『取消』安全退出
        """
        if confirm:
            print("[SettingsPage] ⚠️【警告】正在确认删除设备，点击『确定』...")
            return self.safe_click(SettingsLocators.BTN_DIALOG_CONFIRM, auto_scroll=False)
        else:
            print("[SettingsPage] 🛡️ 取消删除操作，点击『取消』...")
            return self.safe_click(SettingsLocators.BTN_DIALOG_CANCEL, auto_scroll=False)

    # 返回
    def click_back_to_live(self) -> bool:
        """从设备设置页点击左上角返回按钮切回 Live 播放页"""
        print("[SettingsPage] 点击设置页左上角返回按钮切回 Live 界面...")
        if hasattr(SettingsLocators, 'BTN_BACK'):
            return self.safe_click(SettingsLocators.BTN_BACK, auto_scroll=False)
        else:
            # 通用左上角返回图标或 fallback
            return self.safe_click(('id', 'com.xc.sv360:id/left_img'), auto_scroll=False)

        # pages/third_page/setting_page.py

    def get_supported_work_modes(self) -> list:
        """进入工作模式页扫描并返回设置页"""
        # 点击工作模式入口
        self.safe_click(("xpath", "//*[@text='工作模式']"))
        time.sleep(1)

        # 实例化/调用工作模式页扫描方法
        work_mode_page = WorkModePage(self.driver)
        modes = work_mode_page.get_available_modes()  # 或工作模式页的获取列表方法

        # 返回设置页
        work_mode_page.click_back()
        return modes





