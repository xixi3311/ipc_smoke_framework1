# pages/base_page.py
import time
import config
from utils.logger import get_logger


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.logger = get_logger(self.__class__.__name__)

    def kill_app_if_loading_stuck(self, max_wait=120):
        """
        检测"加载中"弹窗，如果超过 max_wait 秒还在，杀 APP 重启
        返回 True: 加载正常消失；False: 超时已杀 APP
        """
        start = time.time()
        while time.time() - start < max_wait:
            # 检测加载中弹窗（ui12 的 XML 特征）
            loading = self.driver(resourceId="com.xc.sv360:id/tvTitle", text="加载中")
            if not loading.exists:
                return True
            time.sleep(2)

        # 超时，强制杀 APP 重启
        print(f"[BasePage] ⚠️ 加载中超过 {max_wait} 秒，强制停止 APP 并重启")
        self.driver.app_stop(config.APP_PACKAGE)
        time.sleep(2)
        self.driver.app_start(config.APP_PACKAGE)
        time.sleep(5)
        # 确保回到首页
        from pages.first_page.home_page import HomePage
        HomePage(self.driver).ensure_back_to_home()
        return False

    def launch_app(self, stop=False):
        """重新启动或拉起应用"""
        print(f"[BasePage] 正在拉起应用: {config.APP_PACKAGE}")
        self.driver.app_start(config.APP_PACKAGE, stop=stop)

    def _is_element_present(self, by, value):
        """内部辅助方法：校验元素当前是否在屏幕可见"""
        if by == 'id':
            return self.driver(resourceId=value).exists
        elif by == 'xpath':
            return self.driver.xpath(value).exists
        elif by == 'text':
            return self.driver(text=value).exists
        return False

    # 兼容 HomePage 里的 _is_element_visible 调取
    _is_element_visible = _is_element_present

    def scroll_into_view(self, locator, max_swipes=3, direction="up"):
        """
        通用滑动查找元素方法：若元素不在当前屏幕，则自动滑动寻找
        :param locator: 元组 ('id'/'xpath'/'text', '值')
        :param max_swipes: 最大滑动次数
        :param direction: 滑动方向 ("up" 向上滑动查看下方区域, "down" 向下滑动)
        """
        by, value = locator

        # 1. 检查当前屏幕是否已存在
        if self._is_element_present(by, value):
            return True

        # 2. 循环滑动查找
        for i in range(max_swipes):
            print(f"[BasePage] 元素未出现，正在第 {i + 1} 次向 '{direction}' 滑动寻找...")
            self.driver.swipe_ext(direction, scale=0.4)
            time.sleep(1)
            if self._is_element_present(by, value):
                print(f"[BasePage] 成功滑动找到目标元素: {locator}")
                return True

        print(f"[BasePage] 达到最大滑动次数 ({max_swipes})，仍未在屏幕找到元素: {locator}")
        return False

    def safe_click(self, locator, timeout=10, auto_scroll=True):
        """
        安全点击方法：默认开启 auto_scroll 自动滑动寻找
        """
        by, value = locator

        # 如果开启自动滑动查找，先尝试将元素滑入视野
        if auto_scroll:
            self.scroll_into_view(locator)

        try:
            if by == 'id':
                el = self.driver(resourceId=value)
                if el.wait(timeout=timeout):
                    el.click()
                    return True
            elif by == 'xpath':
                el = self.driver.xpath(value)
                if el.wait(timeout=timeout):
                    el.click()
                    return True
            elif by == 'text':
                el = self.driver(text=value)
                if el.wait(timeout=timeout):
                    el.click()
                    return True
            else:
                raise ValueError(f"不支持的定位方式: {by}")
        except Exception as e:
            print(f"[BasePage] 点击元素失败 {locator}: {e}")
            return False

        print(f"[BasePage] 未能在 {timeout} 秒内找到元素: {locator}")
        return False

    # 点击输入框输入文本
    def input_text(self, locator, text, clear=True, click_before=True):
        """
        通用输入方法
        :param locator: (by, value)
        :param text: 要输入的文本
        :param clear: 是否清空原有内容
        :param click_before: 是否先点击输入框（触发焦点和键盘）
        """
        by, value = locator
        if click_before:
            self.safe_click(locator, auto_scroll=True)
            time.sleep(0.3)  # 等待键盘弹出
        try:
            if by == 'id':
                el = self.driver(resourceId=value)
                if el.wait(timeout=5):
                    if clear:
                        el.clear_text()
                    el.send_keys(text)
                    return True
            elif by == 'xpath':
                el = self.driver.xpath(value)
                if el.wait(timeout=5):
                    if clear:
                        el.clear_text()
                    el.send_keys(text)
                    return True
            else:
                raise ValueError(f"不支持的定位方式: {by}")
        except Exception as e:
            self.logger.error(f"输入文本失败: {locator}, 错误: {e}")
            return False
        self.logger.error(f"输入框元素未在5秒内出现: {locator}")
        return False


    #右滑动隐藏键盘
    def hide_keyboard(self):
        """模拟从左侧边缘向右滑动的返回手势（全面屏手势）"""
        try:
            # 从屏幕左侧边缘（x=10, y=屏幕一半）向右滑到x=300
            width = self.driver.window_size()[0]
            height = self.driver.window_size()[1]
            self.driver.swipe(10, height // 2, 300, height // 2, duration=0.1)
            time.sleep(0.3)
            self.logger.debug("已执行左边缘滑动返回手势")
            return True
        except Exception as e:
            self.logger.warning(f"滑动返回手势失败: {e}")
            return False





