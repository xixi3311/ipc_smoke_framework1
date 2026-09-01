# pages/third_page/sdcard_replay_ext_page.py
import time
import random
from typing import List
from pages.third_page.sdcard_replay_page import SdCardReplayPage
from locators.third_page_locator.sdcard_replay_ext_locator import SdCardReplayExtLocators
from locators.third_page_locator.sdcard_replay_locator import SdCardReplayLocators  # 新增导入


class SdCardReplayExtPage(SdCardReplayPage):
    """卡回看扩展页面类：事件类型切换、随机事件点击、日期切换，通过加载转圈消失判定出图"""

    def __init__(self, driver):
        super().__init__(driver)
        self.ext = SdCardReplayExtLocators

    # ================= 1. 页面状态检测 =================

    def has_sd_card_video(self) -> bool:
        if self._is_element_present(*self.ext.TV_CENTER_NO_VIDEO):
            self.logger.warning("检测到无录像提示 (UI1)")
            return False
        if self._is_element_present(*self.ext.TIME_RULER) or \
           self._is_element_present(*self.ext.PLAY_TIME_RV):
            self.logger.info("检测到有录像界面 (UI2)")
            return True
        return False

    def is_video_played_out(self) -> bool:
        """检测是否显示'录像已播完' (UI7)"""
        return self._is_element_present(*self.ext.TV_CENTER_NO_VIDEO) and \
               self.driver(resourceId=self.ext.TV_CENTER_NO_VIDEO[1]).text == "录像已播完"

    def wait_for_loading_disappear(self, timeout: int = 10) -> bool:
        """
        等待加载转圈消失，若出现'录像已播完'也视为加载完成
        复用 SdCardReplayLocators.LOADING_LAYOUT（与父类一致）
        """
        self.logger.info(f"等待卡回看加载转圈消失，超时 {timeout}s")
        start = time.time()

        # ✅ 使用已有的定位器，不再重复定义
        if not self._wait_for_element(SdCardReplayLocators.LOADING_LAYOUT, timeout=2):
            self.logger.info("未检测到加载转圈，可能已加载完成")
            return True

        while time.time() - start < timeout:
            if self.is_video_played_out():
                self.logger.info("检测到'录像已播完'，判定加载完成")
                return True
            if not self._is_element_present(*SdCardReplayLocators.LOADING_LAYOUT):
                self.logger.info("加载转圈已消失，判定出图")
                return True
            time.sleep(0.5)

        self.logger.warning(f"加载转圈在 {timeout}s 内未消失")
        return False

    # ================= 2. 事件类型操作 =================

    def _open_event_type_panel(self) -> bool:
        self.logger.info("点击事件类型筛选器，打开面板")
        return self.safe_click(self.ext.IV_VIDEO_TYPE_FILTER, auto_scroll=False)

    def scan_available_event_types(self) -> List[str]:
        if not self._open_event_type_panel():
            self.logger.error("无法打开事件类型面板")
            return []

        time.sleep(0.8)
        type_texts = []
        elements = self.driver.xpath(f"//*[@resource-id='{self.ext.EVENT_TYPE_TEXT[1]}']").all()
        for el in elements:
            txt = el.text.strip()
            if txt and txt != "事件类型":
                type_texts.append(txt)

        unique_types = []
        for t in type_texts:
            if t not in unique_types:
                unique_types.append(t)

        self.logger.info(f"扫描到事件类型: {unique_types}")
        self.driver.press("back")
        time.sleep(0.5)
        return unique_types

    def select_event_type(self, type_name: str) -> bool:
        if not self._open_event_type_panel():
            return False
        time.sleep(0.5)

        locator = ('xpath', f"//*[@resource-id='{self.ext.EVENT_TYPE_TEXT[1]}' and @text='{type_name}']/parent::*")
        if not self.safe_click(locator, auto_scroll=False):
            self.logger.error(f"未找到类型: {type_name}")
            self.driver.press("back")
            return False

        time.sleep(1.5)
        # 等待列表加载
        self._wait_for_event_list_populated(timeout=5)
        return True

    def _wait_for_event_list_populated(self, timeout=5) -> bool:
        start = time.time()
        while time.time() - start < timeout:
            items = self._get_event_items()
            if len(items) > 0:
                self.logger.info(f"事件列表已加载，共 {len(items)} 项")
                return True
            time.sleep(0.5)
        self.logger.warning("事件列表在超时后仍为空")
        return False

    # ================= 3. 事件列表操作 =================

    def _get_event_items(self):
        return self.driver.xpath(self.ext.EVENT_ROOT_VIEW[1]).all()

    def click_random_events_and_verify(self, count: int = 2) -> bool:
        """
        随机点击 count 个事件，通过加载转圈消失或'录像已播完'判定出图
        如果实际可点击事件少于 count，则全部点击并验证
        如果列表为空，返回 True（无事件不算失败，上层应继续遍历）
        """
        self._wait_for_event_list_populated(timeout=5)
        items = self._get_event_items()
        if len(items) == 0:
            self.logger.warning("当前列表无事件可点击，跳过该类型")
            return True  # ✅ 无事件不算失败，继续遍历下一个类型

        # 实际点击数量：取 count 和可用数量的较小值
        actual_count = min(count, len(items))
        selected = random.sample(items, actual_count)
        self.logger.info(f"计划点击 {actual_count} 个事件（共 {len(items)} 个可用）")

        success_count = 0
        for idx, item in enumerate(selected):
            self.logger.info(f"点击事件 #{idx + 1}/{actual_count}")
            item.click()
            time.sleep(1)

            if self.wait_for_loading_disappear(timeout=10):
                self.logger.info(f"事件 #{idx + 1} 出图成功")
                success_count += 1
            else:
                self.logger.warning(f"事件 #{idx + 1} 出图失败")

            time.sleep(0.5)

        # 判定：所有点击的事件都成功则通过
        result = success_count == actual_count
        self.logger.info(f"成功 {success_count}/{actual_count} 个事件，结果: {'通过' if result else '失败'}")
        return result

    # ================= 4. 日期切换操作 =================

    def _open_calendar(self) -> bool:
        self.logger.info("点击日期选择器打开日历")
        return self.safe_click(self.ext.SHOW_DATE_SELECT, auto_scroll=False)

    def _get_calendar_days(self) -> List[str]:
        elements = self.driver.xpath(f"//*[@resource-id='{self.ext.CALENDAR_VIEW[1]}']//*[@text]").all()
        day_texts = [el.text for el in elements if el.text.isdigit()]
        self.logger.info(f"日历中的日期数字: {day_texts}")
        return day_texts

    def click_random_date_and_verify(self, count: int = 2) -> bool:
        if not self._open_calendar():
            self.logger.error("无法打开日历")
            return False

        day_texts = self._get_calendar_days()
        if not day_texts:
            self.logger.warning("未找到日期数字，关闭日历")
            self.driver.press("back")
            return False

        random.shuffle(day_texts)
        success_dates = []
        for day in day_texts:
            if len(success_dates) >= count:
                break
            self.logger.info(f"尝试点击日期: {day}")
            day_locator = ('xpath', f"//*[@resource-id='{self.ext.CALENDAR_VIEW[1]}']//*[@text='{day}']")
            if not self.safe_click(day_locator, auto_scroll=False):
                continue
            time.sleep(1.5)

            # 检查是否有录像事件列表
            if self._is_element_present(*self.ext.PLAY_TIME_RV) and \
               len(self.driver.xpath(self.ext.EVENT_ROOT_VIEW[1]).all()) > 0:
                self.logger.info(f"日期 {day} 有录像，验证出图")
                if self.wait_for_loading_disappear(timeout=10):
                    self.logger.info(f"日期 {day} 出图成功")
                    success_dates.append(day)
                else:
                    self.logger.warning(f"日期 {day} 出图失败")
            else:
                self.logger.info(f"日期 {day} 无录像，继续")

            self.driver.press("back")
            time.sleep(0.5)

        self.driver.press("back")  # 关闭日历
        self.logger.info(f"成功验证 {len(success_dates)} 个日期")
        return len(success_dates) >= count

    # ================= 5. 辅助方法 =================

    def _wait_for_element(self, locator, timeout=5):
        by, value = locator
        start = time.time()
        while time.time() - start < timeout:
            if self._is_element_present(by, value):
                return True
            time.sleep(0.3)
        return False

    def _get_element_text(self, by, value):
        try:
            if by == 'id':
                el = self.driver(resourceId=value)
                if el.exists:
                    return el.text
            elif by == 'xpath':
                el = self.driver.xpath(value)
                if el.exists:
                    return el.text
            elif by == 'text':
                el = self.driver(text=value)
                if el.exists:
                    return el.text
        except:
            pass
        return None