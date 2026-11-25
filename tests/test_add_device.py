# tests/test_add_device.py
import pytest
import allure
import time
import config
import logging
from pages.first_page.home_page import HomePage
from pages.pairing_page.scan_qr_page import ScanQRPage
from pages.pairing_page.manual_input_dialog import ManualInputDialog
from pages.pairing_page.add_device_page import AddDevicePage
from pages.pairing_page.set_wifi_page import SetWifiPage
from pages.pairing_page.connect_wlan_page import ConnectWlanPage
from pages.pairing_page.system_wlan_page import SystemWlanPage
from pages.pairing_page.device_connecting_page import DeviceConnectingPage
from pages.pairing_page.device_name_page import DeviceNamePage
from pages.pairing_page.add_failure_page import AddFailurePage
from pages.pairing_page.device_confirm_page import DeviceConfirmPage
from pages.base_page import BasePage


@allure.epic("IPC 自动化测试框架")
@allure.feature("设备绑定（热点绑定 - SN 输入）")
class TestAddDevice:

    @pytest.fixture(autouse=True)
    def setup_pages(self, driver):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.driver = driver
        self.home_page = HomePage(driver)
        self.scan_qr_page = ScanQRPage(driver)
        self.manual_dialog = ManualInputDialog(driver)
        self.add_device_page = AddDevicePage(driver)
        self.set_wifi_page = SetWifiPage(driver)
        self.connect_wlan_page = ConnectWlanPage(driver)
        self.system_wlan_page = SystemWlanPage(driver)
        self.connecting_page = DeviceConnectingPage(driver)
        self.device_name_page = DeviceNamePage(driver)
        self.failure_page = AddFailurePage(driver)
        # 确保回到首页
        self.home_page.ensure_back_to_home()
        self.device_confirm_page = DeviceConfirmPage(driver)

    @allure.story("设备绑定完整流程（扫码 / 蓝牙）")
    @pytest.mark.smoke
    def test_device_binding(self):
        device_sn = config.DEVICE_SN
        device_name = (
            config.DEVICE_DISPLAY_NAME
            if hasattr(config, "DEVICE_DISPLAY_NAME")
            else config.DEVICE_NAME
        )
        device_type = getattr(config, "DEVICE_TYPE", "wifi")
        binding_type = getattr(config, "BINDING_TYPE", "sn")

        assert binding_type in ("sn", "bluetooth"), \
            f"不支持的绑定入口: {binding_type}"
        assert device_type in ("wifi", "4g"), \
            f"不支持的设备类型: {device_type}"

        # ---------------- 进入绑定入口 ----------------

        sn_route = None

        if binding_type == "bluetooth":
            with allure.step("首页进入添加设备并选择附近蓝牙设备"):
                assert self.home_page.open_add_device(), \
                    "打开添加设备页面失败"
                assert self.add_device_page.is_on_bluetooth_device_list(), \
                    "未进入发现附近设备列表"
                assert self.add_device_page.click_bluetooth_device(
                    config.DEVICE_SN,
                    timeout=30
                ), f"附近设备未发现目标 SN: {config.DEVICE_SN}"
        else:
            with allure.step("扫码页面手动输入设备 SN"):
                assert self.home_page.open_scan_qr(), \
                    "打开扫一扫失败"
                time.sleep(1)
                assert self.scan_qr_page.is_on_scan_qr_page(), \
                    "未进入扫一扫页面"
                assert self.scan_qr_page.click_manual_input(), \
                    "点击手动输入失败"
                time.sleep(0.5)
                assert self.manual_dialog.is_on_dialog(), \
                    "手动输入弹窗未出现"
                assert self.manual_dialog.input_device_id(device_sn), \
                    "输入设备 SN 失败"
                assert self.manual_dialog.click_confirm(), \
                    "点击确定失败"

                if device_type == "wifi":
                    sn_route = self._wait_for_sn_wifi_route(timeout=20)
                    assert sn_route, \
                        "输入 SN 后未进入添加设备页或 Wi-Fi 设置页"

        # ---------------- 按页面状态完成配网 ----------------

        if device_type == "wifi":
            if binding_type == "bluetooth":
                self._bluetooth_binding_flow(device_sn)
            elif sn_route == "add_device":
                self._wifi_binding_flow(start_page="add_device")
            elif sn_route == "set_wifi":
                self._wifi_binding_flow(start_page="set_wifi")
            elif sn_route in ("connecting", "failed", "already_added"):
                self.logger.info(
                    f"输入 SN 后直接进入页面: {sn_route}，"
                    "跳过前置 Wi-Fi 配置流程"
                )
            else:
                pytest.fail(f"无法处理 SN 绑定后的页面状态: {sn_route}")
        else:
            self._4g_binding_flow()

        # ---------------- 等待联网结果 ----------------

        with allure.step("等待配网完成（最长 180 秒）"):
            success, error_msg = self.connecting_page.wait_for_result(timeout=180)

            if success and error_msg == "already_added":
                with allure.step("处理设备已添加提示并验证首页设备"):
                    assert self.device_confirm_page.click_know(), \
                        "关闭已添加提示失败"
                    assert self.home_page.ensure_back_to_home(), \
                        "返回设备首页失败"
                    assert self.home_page.refresh_device_list(), \
                        "刷新首页设备列表失败"
                    assert self.home_page.wait_for_device(device_name), \
                        f"设备 {device_name} 未在首页列表中找到"
                    return

            if not success:
                if self.failure_page.is_on_failure_page():
                    self.failure_page.click_retry()
                    self.home_page.ensure_back_to_home()
                pytest.fail(f"配网失败: {error_msg}")

        time.sleep(1)

        # ---------------- 设置设备名称 ----------------

        with allure.step(f"设置设备名称: {device_name}"):
            assert self.device_name_page.is_on_device_name_page(), \
                "未进入设备名称设置页"
            assert self.device_name_page.input_device_name(device_name), \
                "输入设备名称失败"
            assert self.device_name_page.click_complete(), \
                "点击完成失败"
            time.sleep(2)

        # ---------------- 返回首页并验证绑定结果 ----------------

        with allure.step("返回首页、刷新并验证设备"):
            assert self.home_page.ensure_back_to_home(), \
                "返回设备首页失败"
            assert self.home_page.refresh_device_list(), \
                "刷新首页设备列表失败"
            assert self.home_page.wait_for_device(device_name), \
                f"设备 {device_name} 未在首页列表中找到"

    def _bluetooth_binding_flow(self, device_sn: str):
        """蓝牙发现设备后配置 WiFi，并直接进入设备联网流程"""
        with allure.step(f"蓝牙设备 {device_sn} 配置 WiFi"):
            assert self.set_wifi_page.is_on_set_wifi_page(), \
                "选择蓝牙设备后未进入设置 Wi-Fi 页面"
            assert self.set_wifi_page.input_wifi_ssid(config.WIFI_SSID), \
                "输入 WiFi 名称失败"
            assert self.set_wifi_page.input_wifi_password(config.WIFI_PASSWORD), \
                "输入 WiFi 密码失败"
            assert self.set_wifi_page.click_next(), \
                "点击下一步失败"

    def _wifi_binding_flow(self, start_page="add_device"):
        """根据 SN 后的页面状态完成 Wi-Fi 绑定流程"""

        if start_page == "add_device":
            with allure.step("添加设备页勾选提示音并选择热点配网"):
                assert self.add_device_page.wait_until(
                    self.add_device_page.is_on_add_device_page,
                    timeout=15
                ), "未进入添加设备页"
                assert self.add_device_page.check_hear_alert(True), \
                    "勾选听提示失败"
                assert self.add_device_page.click_hotspot_pairing(), \
                    "点击热点配网失败"
                assert self.set_wifi_page.wait_for_set_wifi_page(
                    timeout=15
                ), "点击热点配网后未进入设置 Wi-Fi 页面"

        elif start_page == "set_wifi":
            assert self.set_wifi_page.wait_for_set_wifi_page(timeout=15), \
                "输入 SN 后未进入设置 Wi-Fi 页面"

        else:
            pytest.fail(f"不支持的 Wi-Fi 流程起始页面: {start_page}")

        with allure.step(f"设置 Wi-Fi: {config.WIFI_SSID}"):
            assert self.set_wifi_page.input_wifi_ssid(config.WIFI_SSID), \
                "输入 Wi-Fi 名称失败"
            assert self.set_wifi_page.input_wifi_password(
                config.WIFI_PASSWORD
            ), "输入 Wi-Fi 密码失败"
            assert self.set_wifi_page.click_next(), \
                "点击下一步失败"

        route = self._wait_for_wifi_next_route(timeout=20)

        if route in ("connecting", "failed", "already_added"):
            self.logger.info(
                f"点击下一步后进入页面: {route}，跳过设备热点流程"
            )
            return

        assert route == "connect_wlan", \
            f"点击下一步后页面状态异常: {route}"

        with allure.step("连接设备 WLAN"):
            assert self.connect_wlan_page.is_on_connect_wlan_page(), \
                "未进入连接设备 WLAN 页面"
            assert self.connect_wlan_page.click_connect_wlan(), \
                "点击连接设备 WLAN 失败"
            time.sleep(2)

        with allure.step(f"连接热点 SV-{config.DEVICE_SN}"):
            assert self.system_wlan_page.is_on_system_wlan_page(), \
                "未进入系统 WLAN 页面"
            assert self.system_wlan_page.connect_to_device_hotspot(
                config.DEVICE_SN
            ), f"连接设备热点 SV-{config.DEVICE_SN} 失败"
            self.driver.press("back")
            time.sleep(2)

    def _wait_for_sn_wifi_route(self, timeout=20):
        """等待手动输入 SN 后进入 UI3、UI5 或配网结果页面"""
        end_time = time.monotonic() + timeout

        while time.monotonic() < end_time:
            if self.device_confirm_page.is_already_added_page():
                return "already_added"

            if self.failure_page.is_on_failure_page():
                return "failed"

            if self.add_device_page.is_on_add_device_page():
                return "add_device"

            if self.set_wifi_page.is_on_set_wifi_page():
                return "set_wifi"

            if self.connecting_page.is_on_connecting_page(timeout=0.1):
                return "connecting"

            time.sleep(0.3)

        return ""

    def _wait_for_wifi_next_route(self, timeout=20):
        """等待 Wi-Fi 配置提交后进入 UI6、UI8 或配网结果页面"""
        end_time = time.monotonic() + timeout

        while time.monotonic() < end_time:
            if self.device_confirm_page.is_already_added_page():
                return "already_added"

            if self.failure_page.is_on_failure_page():
                return "failed"

            if self.connect_wlan_page.is_on_connect_wlan_page():
                return "connect_wlan"

            if self.connecting_page.is_on_connecting_page(timeout=0.1):
                return "connecting"

            time.sleep(0.3)

        return ""

    def _4g_binding_flow(self):
        """4G 设备配网流程：跳过 WiFi 配置，直接进入设备联网中"""
        allure.attach("4G 设备配网流程（跳过 WiFi 配置）", name="设备类型", attachment_type=allure.attachment_type.TEXT)

        # 4G 设备输入 SN 后直接进入联网中页面，无需任何额外操作
        # 等待联网中页面出现（由主流程的 connecting_page.is_on_connecting_page 负责）
        self.logger.info("4G 设备已进入配网流程，等待设备联网中页面...")
        time.sleep(1)

