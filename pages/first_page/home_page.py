# pages/first_page/home_page.py
import time
import re
from typing import List
from pages.base_page import BasePage
from locators.first_page_locator.home_locator import HomeLocators


class HomePage(BasePage):

    # ---------------- 首页判断与安全返回 ----------------
    def is_on_home_page(self) -> bool:
        """
        判断当前页面是否处于设备首页（宽松判断）
        满足以下任一条件即认为是首页：
        1. 底部"设备"Tab 被选中（最可靠）
        2. 顶部"所有设备"标题存在
        3. 加号按钮存在（兜底）
        """
        # 1. 检查底部"设备"Tab 是否被选中（最可靠）
        device_tab = self.driver(text="设备")
        if device_tab.exists and device_tab.info.get("selected", False):
            return True

        # 2. 检查顶部的"所有设备"标题（注意：_is_element_visible 需要两个参数）
        if self._is_element_visible('xpath', "//*[@resource-id='com.xc.sv360:id/tvAllDevice']"):
            return True

        # 3. 降级：检查加号按钮是否存在
        if self._is_element_visible(*HomeLocators.Home_TOP_PLUS_BTN):
            return True

        return False

    def ensure_back_to_home(self, max_retries=3) -> bool:
        """确保应用切回设备首页"""
        if self.is_on_home_page():
            print("[HomePage] 确认当前已处于设备首页 🟢")
            return True

        device_tab = self.driver(text="设备")
        if device_tab.exists:
            print("[HomePage] 发现处于主框架其他 Tab 页，尝试点击底部【设备】Tab")
            try:
                device_tab.click()
                time.sleep(0.8)
                if self.is_on_home_page():
                    print("[HomePage] ✅ 成功点击 Tab 切回设备首页！")
                    return True
            except Exception as e:
                print(f"[HomePage] 点击底部【设备】Tab失败，继续尝试返回: {e}")

        for i in range(max_retries):
            print(
                f"[HomePage] 当前不在首页，正在尝试第 {i + 1} 次"
                "按 Back 键切回首页..."
            )
            self.driver.press("back")
            time.sleep(1.2)

            # Back 可能已经直接回到首页，先判断，避免误点异常坐标
            if self.is_on_home_page():
                print("[HomePage] ✅ 成功切回设备首页！")
                return True

            device_tab = self.driver(text="设备")
            if device_tab.exists:
                try:
                    device_tab.click()
                    time.sleep(0.8)
                except Exception as e:
                    print(f"[HomePage] 点击底部【设备】Tab失败: {e}")

            if self.is_on_home_page():
                print("[HomePage] ✅ 成功切回设备首页！")
                return True

        print("[HomePage] ⚠️ 无法通过 Back 键返回首页，执行强制重启 App...")
        self.launch_app(stop=True)
        time.sleep(3)
        return self.is_on_home_page()

    # ---------------- 设备列表获取 ----------------
    def get_current_screen_device_names(self) -> List[str]:
        """获取【当前屏幕】所有可见设备的名称列表"""
        elements = self.driver.xpath(HomeLocators.ALL_DEVICE_NAMES[1]).all()
        return [el.text for el in elements if el.text]

    # ---------------- 设备状态检查 ----------------
    def check_device_offline_status(self, device_name: str) -> dict:
        """检查设备是否离线"""
        self.scroll_into_view(HomeLocators.get_device_name_locator(device_name))

        locator = HomeLocators.get_offline_tv_by_device_name(device_name)
        offline_el = self.driver.xpath(locator[1])

        if offline_el.exists:
            raw_text = offline_el.text
            match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', raw_text)
            offline_time = match.group(0) if match else raw_text

            print(f"[HomePage] ⚠️ 设备 [{device_name}] 当前处于【离线】状态！({raw_text})")
            return {
                "is_offline": True,
                "offline_time": offline_time,
                "raw_text": raw_text
            }
        else:
            print(f"[HomePage] 🟢 设备 [{device_name}] 当前处于【在线】状态")
            return {
                "is_offline": False,
                "offline_time": None,
                "raw_text": None
            }

    # ---------------- 播放与菜单操作 ----------------
    def click_play_button(self, device_name: str) -> bool:
        """
        点击指定设备卡片中间的播放按钮。

        原来的问题：

        1. 点击一次后没有确认是否进入 Live 页面；
        2. 点击失败时直接返回，后续代码继续执行；
        3. 设备卡片正在刷新时，XPath 可能暂时找不到按钮；
        4. 播放按钮点击无效时，后续仍然继续检测 Live 页面。

        新逻辑：

        1. 先滑动查找播放按钮；
        2. 最多点击 3 次；
        3. 每次点击后确认 Live 页面是否出现；
        4. 未进入 Live 页面时才允许重试；
        5. 最终失败才返回 False。
        """

        from pages.second_page.live_page import LivePage

        print(
            f"[HomePage] 点击设备 [{device_name}] "
            "画面中央的 ▶️ 播放按钮"
        )

        locator = HomeLocators.get_play_btn_by_device_name(
            device_name
        )

        # 设备列表可能发生滚动，先确保播放按钮进入屏幕
        if not self.scroll_into_view(
                locator,
                max_swipes=5,
                direction="up",
        ):
            print(
                f"[HomePage] 未找到设备 [{device_name}] 的播放按钮"
            )
            return False

        for attempt in range(1, 4):
            print(
                f"[HomePage] 播放按钮点击，第 {attempt}/3 次"
            )

            # 单次点击失败时，进入下一次重试
            clicked = self.safe_click(
                locator,
                timeout=5,
                auto_scroll=False,
                retries=1,
            )

            if not clicked:
                time.sleep(1)
                continue

            # 点击后必须确认 Live 页面出现
            live_page = LivePage(self.driver)

            if live_page.wait_until(
                    live_page.is_on_live_page,
                    timeout=8,
            ):
                print("[HomePage] 已成功进入 Live 页面")
                return True

            # 点击成功但页面没有跳转，可能是点击没有真正生效
            print(
                "[HomePage] 点击播放后未进入 Live 页面，"
                "准备重试"
            )
            time.sleep(1)

        print(
            f"[HomePage] 多次点击播放仍未进入 Live 页面: "
            f"{device_name}"
        )
        return False

    def click_device_more_menu(self, device_name: str) -> bool:
        """点击指定设备卡片右下角的 '⋮' 按钮"""
        print(f"[HomePage] 点击设备 [{device_name}] 右下角 '⋮' 按钮")
        return self.safe_click(HomeLocators.get_more_btn_by_device_name(device_name))

    def check_more_menu_settings_exist(self) -> bool:
        """检查 '⋮' 弹出菜单中的 '设置' 是否存在"""
        return self._is_element_visible(*HomeLocators.MORE_MENU_SETTINGS)

    def click_more_menu_settings(self) -> bool:
        """点击弹出菜单中的 '设置'"""
        print("[HomePage] 点击弹出菜单中的 '设置'")
        return self.safe_click(HomeLocators.MORE_MENU_SETTINGS, auto_scroll=False)

    def open_add_device(self) -> bool:
        """修复括号问题：点击 '+' 并选择 '添加设备'"""
        self.safe_click(HomeLocators.Home_TOP_PLUS_BTN, auto_scroll=False)
        time.sleep(0.5)
        return self.safe_click(HomeLocators.MENU_ADD_DEVICE, auto_scroll=False)

    def open_scan_qr(self) -> bool:
        """点击 '+' 并选择 '扫一扫'"""
        self.safe_click(HomeLocators.Home_TOP_PLUS_BTN, auto_scroll=False)
        time.sleep(0.5)
        return self.safe_click(HomeLocators.MENU_SCAN_QR, auto_scroll=False)

    # ---------------- 首页刷新与设备验证 ----------------
    def refresh_device_list(self) -> bool:
        self.logger.info("下拉刷新首页设备列表")
        try:
            self.driver.swipe_ext("down", scale=0.3)
            time.sleep(2)
            return self.is_on_home_page()
        except Exception as e:
            self.logger.warning(f"刷新首页设备列表失败: {e}")
            return False

    def wait_for_device(self, device_name: str, timeout=20) -> bool:
        locator = HomeLocators.get_device_name_locator(device_name)
        return self.wait_until(
            lambda: self._is_element_present(*locator),
            timeout=timeout
        )

    # ---------------- 设备删除状态检查 ----------------
    def wait_for_device_absent(self, device_name: str, timeout=15) -> bool:
        locator = HomeLocators.get_device_name_locator(device_name)
        return self.wait_until(
            lambda: not self._is_element_present(*locator),
            timeout=timeout
        )