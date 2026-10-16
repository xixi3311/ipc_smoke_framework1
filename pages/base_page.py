# pages/base_page.py
import time
import config
from utils.logger import get_logger


class BasePage:
    """所有 Page 对象的基类"""

    def __init__(self, driver):
        self.driver = driver
        self.logger = get_logger(self.__class__.__name__)

    # ---------------- 元素查找与等待 ----------------
    def _get_element(self, locator):
        """根据定位器获取元素对象"""
        by, value = locator

        if by == "id":
            return self.driver(resourceId=value)
        elif by == "xpath":
            return self.driver.xpath(value)
        elif by == "text":
            return self.driver(text=value)

        raise ValueError(f"不支持的定位方式: {by}")

    def _is_element_present(self, by, value):
        """判断元素当前是否存在"""
        try:
            return self._get_element((by, value)).exists
        except Exception as e:
            self.logger.debug(f"检查元素是否存在失败: {(by, value)}, {e}")
            return False

    # 兼容原有页面对象对该方法的调用
    _is_element_visible = _is_element_present

    def wait_until(self, condition, timeout=10, interval=0.2):
        """在指定时间内重复检查条件是否成立"""
        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                if condition():
                    return True
            except Exception as e:
                self.logger.debug(f"等待条件检查异常: {e}")

            time.sleep(interval)

        return False

    def wait_element(self, locator, timeout=10):
        """等待指定元素出现"""
        return self.wait_until(
            lambda: self._is_element_present(*locator),
            timeout=timeout
        )

    # ---------------- 滑动查找 ----------------
    def scroll_into_view(self, locator, max_swipes=3, direction="up"):
        """
        通用滑动查找元素方法：若元素不在当前屏幕，则滑动查找。
        direction 使用 "up" 表示向上滑动查看下方区域。
        """

        # 先检查当前屏幕，避免进行不必要的滑动
        if self._is_element_present(*locator):
            return True

        # 当前屏幕未找到元素，按指定方向滑动查找
        for i in range(max_swipes):
            print(
                f"[BasePage] 元素未出现，正在第 {i + 1} 次"
                f"向 '{direction}' 滑动寻找..."
            )

            try:
                self.driver.swipe_ext(direction, scale=0.4)
            except Exception as e:
                self.logger.warning(f"滑动查找失败: {e}")
                continue

            time.sleep(0.8)

            if self._is_element_present(*locator):
                print(f"[BasePage] 成功滑动找到目标元素: {locator}")
                return True

        print(
            f"[BasePage] 达到最大滑动次数 ({max_swipes})，"
            f"仍未在屏幕找到元素: {locator}"
        )
        return False

    # ---------------- 安全点击 ----------------
    def safe_click(self, locator, timeout=10, auto_scroll=True,
                   retries=3, retry_interval=0.8):
        """
        安全点击元素。元素暂时不可用或点击异常时进行有限次数重试。

        auto_scroll 开启时，会先滑动查找元素；
        retries 控制点击尝试次数，避免一次偶发点击失败就中断流程。
        """

        # 开启自动滑动时，先把元素滑入当前屏幕
        if auto_scroll and not self.scroll_into_view(locator):
            return False

        # 点击失败时进行有限次数重试
        for attempt in range(1, retries + 1):
            try:
                element = self._get_element(locator)

                if not element.wait(timeout=timeout):
                    print(
                        f"[BasePage] 第 {attempt}/{retries} 次等待元素超时: "
                        f"{locator}"
                    )
                    time.sleep(retry_interval)
                    continue

                element.click()
                time.sleep(0.5)
                return True

            except Exception as e:
                print(
                    f"[BasePage] 第 {attempt}/{retries} 次点击失败 "
                    f"{locator}: {e}"
                )
                time.sleep(retry_interval)

        print(f"[BasePage] 多次点击仍失败: {locator}")
        return False

    def click_and_wait_for(self, click_locator, target_condition,
                           click_timeout=5, page_timeout=8, retries=3):
        """点击元素后等待目标页面出现，未出现时再重试点击"""

        for attempt in range(1, retries + 1):
            print(f"[BasePage] 执行点击跳转，第 {attempt}/{retries} 次")

            clicked = self.safe_click(
                click_locator,
                timeout=click_timeout,
                auto_scroll=False,
                retries=1
            )

            if not clicked:
                time.sleep(0.8)
                continue

            # 点击后检查目标页面是否真的出现
            if self.wait_until(target_condition, timeout=page_timeout):
                return True

            print("[BasePage] 点击后目标页面未出现，准备重试")
            time.sleep(0.8)

        return False

    # ---------------- 文本输入 ----------------
    def input_text(self, locator, text, clear=True, click_before=True):
        """通用输入文本方法"""

        if click_before:
            if not self.safe_click(locator, auto_scroll=True):
                return False
            time.sleep(0.3)

        try:
            element = self._get_element(locator)

            if not element.wait(timeout=5):
                return False

            if clear:
                element.clear_text()

            element.send_keys(text)
            return True

        except Exception as e:
            self.logger.error(f"输入文本失败: {locator}, 错误: {e}")
            return False

    # ---------------- 键盘操作 ----------------
    def hide_keyboard(self):
        """模拟从屏幕左侧边缘向右滑动，隐藏软键盘"""
        try:
            width = self.driver.window_size()[0]
            height = self.driver.window_size()[1]
            self.driver.swipe(10, height // 2, min(300, width - 1),
                              height // 2, duration=0.1)
            time.sleep(0.3)
            self.logger.debug("已执行左侧边缘滑动手势")
            return True
        except Exception as e:
            self.logger.warning(f"隐藏键盘失败: {e}")
            return False

    # ---------------- 应用启动与加载检测 ----------------
    def launch_app(self, stop=False):
        """重新启动或拉起应用"""
        print(f"[BasePage] 正在拉起应用: {config.APP_PACKAGE}")
        self.driver.app_start(config.APP_PACKAGE, stop=stop)

    def kill_app_if_loading_stuck(self, max_wait=120):
        """
        检测应用是否长时间停留在加载状态。
        超时后停止并重新启动应用，最后尝试回到首页。
        """

        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                loading = self.driver(
                    resourceId=f"{config.APP_PACKAGE}:id/tvTitle",
                    text="加载中"
                )

                if not loading.exists:
                    return True
            except Exception as e:
                self.logger.debug(f"检测加载状态失败: {e}")

            time.sleep(2)

        print(f"[BasePage] 加载超过 {max_wait} 秒，强制停止并重启 APP")
        self.driver.app_stop(config.APP_PACKAGE)
        time.sleep(2)
        self.driver.app_start(config.APP_PACKAGE)
        time.sleep(5)

        # 重启后尝试回到设备首页
        from pages.first_page.home_page import HomePage
        HomePage(self.driver).ensure_back_to_home()
        return False