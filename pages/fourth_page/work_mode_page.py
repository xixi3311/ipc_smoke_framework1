# pages/fourth_page/work_mode_page.py
import time
from typing import List, Dict
from pages.base_page import BasePage
from locators.fourth_page_locator.work_mode_locator import WorkModeLocators


class WorkModePage(BasePage):
    """工作模式页面类"""

    # 对应 App 固定的 5 种模式编号
    MODE_INDICES = [1, 2, 3, 4, 5]

    def is_on_work_mode_page(self) -> bool:
        """校验是否处于工作模式选择页面"""
        start_time = time.time()
        while time.time() - start_time < 3:
            if self._is_element_present(*WorkModeLocators.TITLE_WORK_MODE) or \
               self.driver(resourceId=f"{WorkModeLocators.PKG}:id/aovWorkMode2Tv").exists:
                return True
            time.sleep(0.5)
        return False

    def scan_device_modes(self, timeout: float = 3.0) -> Dict[str, str]:
        """
        【精准死穴识别】通过 1~5 固有卡片 ID 动态扫描设备当前呈现的工作模式
        返回结构: {'常电模式': 'com.xc.sv360:id/aovWorkMode2Cb', ...}
        """
        detected_modes = {}
        pkg = getattr(WorkModeLocators, "PKG", "com.xc.sv360")

        # 1. 等待界面首个模式节点加载呈现
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.driver(resourceId=f"{pkg}:id/aovWorkMode2Tv").exists or \
               self.driver(resourceId=f"{pkg}:id/aovWorkMode1Tv").exists:
                break
            time.sleep(0.3)

        # 2. 遍历 1~5 号可能存在的模式 Tv 节点
        for idx in self.MODE_INDICES:
            tv_id = f"{pkg}:id/aovWorkMode{idx}Tv"
            cb_id = f"{pkg}:id/aovWorkMode{idx}Cb"

            elem = self.driver(resourceId=tv_id)
            if elem.exists:
                try:
                    # 获取文本
                    mode_text = elem.info.get("text", "").strip()
                    if mode_text:
                        detected_modes[mode_text] = cb_id
                except Exception as e:
                    print(f"[WorkModePage] ⚠️ 解析 id={tv_id} 节点失败: {e}")

        print(f"[WorkModePage] 🔍 动态扫描到的当前设备支持的工作模式: {list(detected_modes.keys())}")
        return detected_modes

    def get_available_modes(self) -> List[str]:
        """获取当前设备支持的所有工作模式名称列表"""
        modes_map = self.scan_device_modes()
        return list(modes_map.keys())

    def select_mode(self, mode_name: str, max_retries: int = 2) -> bool:
        """
        【精准击中逻辑】点击对应模式右侧 RadioButton，并校验 checked 属性
        """
        print(f"[WorkModePage] 🎯 准备切换工作模式为: 『{mode_name}』...")

        modes_map = self.scan_device_modes()
        if mode_name not in modes_map:
            print(f"[WorkModePage] ❌ 当前设备不支持模式『{mode_name}』，可选列表: {list(modes_map.keys())}")
            return False

        cb_id = modes_map[mode_name]
        radio_btn = self.driver(resourceId=cb_id)

        # 1. 已是选中状态直接返回
        if radio_btn.exists and radio_btn.info.get("checked", False):
            print(f"[WorkModePage] ℹ️ 模式『{mode_name}』当前处于选中状态，无需重复点击")
            return True

        # 2. 尝试精准点击
        for attempt in range(1, max_retries + 1):
            print(f"[WorkModePage] 👆 尝试第 {attempt} 次点击 RadioButton ({cb_id})...")

            if radio_btn.exists:
                radio_btn.click()
            else:
                self.safe_click(WorkModeLocators.get_radio_btn_by_mode_name(mode_name), auto_scroll=True)

            time.sleep(1.5)

            # 3. 校验 checked 状态
            if radio_btn.exists and radio_btn.info.get("checked", False):
                print(f"[WorkModePage] ✅ 模式『{mode_name}』切换成功！")
                return True

            print(f"[WorkModePage] ⚠️ 第 {attempt} 次点击未切换成功，正在重试...")

        print(f"[WorkModePage] ❌ 切换工作模式『{mode_name}』失败！")
        return False

    def click_back_to_settings(self) -> bool:
        """从工作模式页返回设备设置页"""
        print("[WorkModePage] 点击左上角返回按钮回到设置页...")
        return self.safe_click(WorkModeLocators.BTN_BACK, auto_scroll=False)


