# pages/fourth_page/device_info_page.py
import os
import json
import time
import config
from typing import Dict, Optional, Tuple
from pages.base_page import BasePage
from locators.fourth_page_locator.device_info_locator import DeviceInfoLocators


class DeviceInfoPage(BasePage):
    """设备信息页面类"""

    def __init__(self, driver):
        super().__init__(driver)
        self.loc = DeviceInfoLocators
        self.battery_file = config.BATTERY_STATE_FILE
        os.makedirs(os.path.dirname(self.battery_file), exist_ok=True)

    # ================= 1. 页面导航 =================

    def enter_device_info(self, max_swipes: int = 5) -> bool:
        """
        在设置页下滑并点击'设备信息'入口
        """
        self.logger.info("正在查找并点击'设备信息'入口...")
        if self.scroll_into_view(self.loc.DEVICE_INFO_ENTRY, max_swipes=max_swipes):
            if self.safe_click(self.loc.DEVICE_INFO_ENTRY, auto_scroll=False):
                time.sleep(1.0)
                return True
        self.logger.error("在设置页未找到'设备信息'入口")
        return False

    def is_on_device_info_page(self, timeout: int = 10) -> bool:
        """
        校验是否处于设备信息页面（等待内容加载完成）
        等待设备名称或设备ID出现，确保内容已加载
        """
        self.logger.info("正在校验是否进入设备信息页...")
        start = time.time()
        while time.time() - start < timeout:
            # 检查内容区域是否加载完成（设备名称或设备ID有文本）
            name_el = self.driver(resourceId=self.loc.DEVICE_NAME_TV[1])
            id_el = self.driver(resourceId=self.loc.DEVICE_ID_TV[1])

            name_text = name_el.info.get('text', '').strip() if name_el.exists else ''
            id_text = id_el.info.get('text', '').strip() if id_el.exists else ''

            if name_text:
                self.logger.info(f"已进入设备信息页，设备名称: {name_text}")
                return True
            if id_text:
                self.logger.info(f"已进入设备信息页，设备ID: {id_text}")
                return True

            # 降级：检查标题是否存在（兜底）
            if self._is_element_present(*self.loc.TITLE_DEVICE_INFO):
                time.sleep(0.5)
                continue

            time.sleep(0.3)

        self.logger.warning("设备信息页内容加载超时")
        return False

    def click_back_to_settings(self) -> bool:
        """从设备信息页返回设置页"""
        self.logger.info("点击返回按钮回到设置页")
        return self.safe_click(self.loc.BTN_BACK, auto_scroll=False)

    def click_back_to_live(self) -> bool:
        """从设备信息页连续返回直至 Live 页（含设置页返回）"""
        self.logger.info("从设备信息页返回 Live 页")
        self.click_back_to_settings()
        time.sleep(0.5)
        from locators.second_page_locator.live_locator import LiveLocators
        return self.safe_click(LiveLocators.BTN_BACK, auto_scroll=False)

    # ================= 2. 设备类型判断 =================

    def get_device_type(self) -> str:
        """判断当前设备类型，返回 'wifi' 或 '4g'"""
        if self._is_element_present(*self.loc.DEVICE_WIFI_TV):
            self.logger.info("检测到 WiFi 设备 (UI2)")
            return "wifi"
        elif self._is_element_present(*self.loc.DEVICE_ICCID_TV):
            self.logger.info("检测到 4G 设备 (UI3)")
            return "4g"
        else:
            self.logger.warning("无法判断设备类型，默认当作 WiFi 设备")
            return "wifi"

    # ================= 3. 获取设备信息 =================

    def _wait_for_text(self, locator, timeout: int = 5) -> str:
        """等待元素出现并有文本，返回文本内容"""
        by, value = locator
        start = time.time()
        while time.time() - start < timeout:
            try:
                if by == 'id':
                    el = self.driver(resourceId=value)
                    if el.exists:
                        text = el.info.get('text', '').strip()
                        if text:
                            return text
                elif by == 'xpath':
                    el = self.driver.xpath(value)
                    if el.exists:
                        text = el.info.get('text', '').strip()
                        if text:
                            return text
            except:
                pass
            time.sleep(0.3)
        return ""

    def _get_text(self, locator) -> str:
        """安全获取元素文本（直接获取，不等待）"""
        by, value = locator
        try:
            if by == 'id':
                el = self.driver(resourceId=value)
                if el.exists:
                    return el.info.get('text', '').strip()
            elif by == 'xpath':
                el = self.driver.xpath(value)
                if el.exists:
                    return el.info.get('text', '').strip()
        except:
            pass
        return ""

    def _parse_battery(self, text: str) -> int:
        """从 '92%' 格式解析出数字 92"""
        if not text:
            return -1
        try:
            return int(text.replace('%', '').strip())
        except:
            return -1

    def get_wifi_device_info(self) -> Dict[str, any]:
        """获取 WiFi 设备信息 (UI2)"""
        self.logger.info("正在获取 WiFi 设备信息...")
        info = {
            "device_name": self._wait_for_text(self.loc.DEVICE_NAME_TV, timeout=3),
            "device_id": self._wait_for_text(self.loc.DEVICE_ID_TV, timeout=3),
            "wifi_network": self._wait_for_text(self.loc.DEVICE_WIFI_TV, timeout=3),
            "mac_address": self._wait_for_text(self.loc.DEVICE_MAC_TV, timeout=3),
            "battery": self._parse_battery(self._wait_for_text(self.loc.DEVICE_BATTERY_TV, timeout=3)),
        }
        self.logger.info(f"获取到设备信息: {info}")
        return info

    def get_4g_device_info(self) -> Dict[str, any]:
        """获取 4G 设备信息 (UI3)"""
        self.logger.info("正在获取 4G 设备信息...")
        info = {
            "device_name": self._wait_for_text(self.loc.DEVICE_NAME_TV, timeout=3),
            "device_id": self._wait_for_text(self.loc.DEVICE_ID_TV, timeout=3),
            "iccid": self._wait_for_text(self.loc.DEVICE_ICCID_TV, timeout=3),
            "battery": self._parse_battery(self._wait_for_text(self.loc.DEVICE_BATTERY_TV, timeout=3)),
        }
        self.logger.info(f"获取到设备信息: {info}")
        return info

    # ================= 4. 电量差值校验 =================

    def _load_battery_state(self, device_sn: str) -> Optional[int]:
        """从 JSON 文件加载指定设备的上一轮电量"""
        if not os.path.exists(self.battery_file):
            self.logger.info("电量状态文件不存在，首次运行")
            return None
        try:
            with open(self.battery_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            last_battery = data.get(device_sn, {}).get("last_battery")
            if last_battery is not None:
                self.logger.info(f"读取到设备 {device_sn} 上一轮电量: {last_battery}%")
            else:
                self.logger.info(f"设备 {device_sn} 无历史电量记录")
            return last_battery
        except Exception as e:
            self.logger.warning(f"读取电量状态文件失败: {e}")
            return None

    def _save_battery_state(self, device_sn: str, battery: int) -> None:
        """保存当前电量到 JSON 文件"""
        try:
            data = {}
            if os.path.exists(self.battery_file):
                with open(self.battery_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            from datetime import datetime
            data[device_sn] = {
                "last_battery": battery,
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(self.battery_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"已保存设备 {device_sn} 电量: {battery}%")
        except Exception as e:
            self.logger.warning(f"保存电量状态失败: {e}")

    def verify_battery_delta(self, current_battery: int, device_sn: str) -> Tuple[bool, int, Optional[int]]:
        """校验电量差值是否超过阈值"""
        if current_battery < 0:
            self.logger.warning("当前电量获取失败，跳过差值校验")
            return True, 0, None

        last_battery = self._load_battery_state(device_sn)

        if last_battery is None:
            self.logger.info(f"首次获取设备 {device_sn} 电量: {current_battery}%，跳过差值校验")
            self._save_battery_state(device_sn, current_battery)
            return True, 0, None

        delta = abs(current_battery - last_battery)
        max_delta = config.MAX_BATTERY_DELTA

        self.logger.info(f"电量对比: 当前 {current_battery}% vs 上一轮 {last_battery}%，差值 {delta}%")

        if delta <= max_delta:
            self.logger.info(f"✅ 电量差值 {delta}% ≤ {max_delta}%，校验通过")
            self._save_battery_state(device_sn, current_battery)
            return True, delta, last_battery
        else:
            self.logger.error(f"❌ 电量差值 {delta}% > {max_delta}%，校验失败")
            self._save_battery_state(device_sn, current_battery)
            return False, delta, last_battery