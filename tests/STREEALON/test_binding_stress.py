import os
import time
import allure
import pytest
import config
from pages.first_page.home_page import HomePage
from pages.second_page.live_page import LivePage
from pages.third_page.setting_page import SettingsPage
from pages.pairing_page.scan_qr_page import ScanQRPage
from pages.pairing_page.manual_input_dialog import ManualInputDialog
from pages.pairing_page.add_device_page import AddDevicePage
from pages.pairing_page.set_wifi_page import SetWifiPage
from pages.pairing_page.connect_wlan_page import ConnectWlanPage
from pages.pairing_page.system_wlan_page import SystemWlanPage
from pages.pairing_page.device_connecting_page import DeviceConnectingPage
from pages.pairing_page.device_name_page import DeviceNamePage
from pages.pairing_page.device_confirm_page import DeviceConfirmPage
from pages.pairing_page.add_failure_page import AddFailurePage




@allure.epic("IPC 自动化测试框架")
@allure.feature("绑定压测")
class TestBindingStress:

    @pytest.fixture(autouse=True)
    def setup_pages(self, driver):
        self.driver = driver
        self.home_page = HomePage(driver)
        self.live_page = LivePage(driver)
        self.settings_page = SettingsPage(driver)
        self.scan_qr_page = ScanQRPage(driver)
        self.manual_dialog = ManualInputDialog(driver)
        self.add_device_page = AddDevicePage(driver)
        self.set_wifi_page = SetWifiPage(driver)
        self.connect_wlan_page = ConnectWlanPage(driver)
        self.system_wlan_page = SystemWlanPage(driver)
        self.connecting_page = DeviceConnectingPage(driver)
        self.device_name_page = DeviceNamePage(driver)
        self.device_confirm_page = DeviceConfirmPage(driver)
        self.failure_page = AddFailurePage(driver)
        self.home_page.ensure_back_to_home()

    @allure.story("按配置绑定、验证 Live 出图并删除设备")
    @pytest.mark.smoke
    def test_binding_preview_and_delete(self):
        try:
            with allure.step("按配置选择绑定入口并完成配网"):
                self._bind_device()

            with allure.step("返回首页并确认设备已出现"):
                assert self.home_page.ensure_back_to_home(), \
                    "返回首页失败"
                assert self.home_page.refresh_device_list(), \
                    "刷新首页设备列表失败"
                assert self.home_page.wait_for_device(config.DEVICE_NAME), \
                    f"首页未找到设备: {config.DEVICE_NAME}"

            with allure.step("进入 Live 并确认绑定后成功出图"):
                self._verify_live_preview()

            with allure.step("删除设备并确认首页已移除"):
                self._delete_device()

        except Exception:
            self._cleanup_bound_device()
            raise

    # ---------------- 按配置选择绑定流程 ----------------
    def _bind_device(self):
        binding_type = config.BINDING_TYPE
        device_type = config.DEVICE_TYPE
        sn_route = None

        assert binding_type in ("sn", "bluetooth"), \
            f"不支持的绑定入口: {binding_type}"
        assert device_type in ("wifi", "4g"), \
            f"不支持的设备类型: {device_type}"
        assert not (binding_type == "bluetooth" and device_type == "4g"), \
            "当前未配置 4G 设备的蓝牙绑定流程"

        # ---------------- 进入绑定入口 ----------------

        if binding_type == "bluetooth":
            self._open_bluetooth_device()
        else:
            self._open_manual_sn_entry()

            if device_type == "wifi":
                sn_route = self._wait_for_sn_wifi_route(timeout=20)
                assert sn_route, \
                    "输入 SN 后未进入添加设备页或 Wi-Fi 设置页"

        # ---------------- 按设备类型和页面状态完成配网 ----------------

        if device_type == "4g":
            self._bind_4g_device()

        elif binding_type == "bluetooth":
            self._bind_bluetooth_wifi_device()

        elif sn_route == "add_device":
            self._bind_wifi_device(start_page="add_device")

        elif sn_route == "set_wifi":
            self._bind_wifi_device(start_page="set_wifi")

        elif sn_route in ("connecting", "failed", "already_added"):
            print(
                f"[BindingStress] 输入 SN 后进入页面: {sn_route}，"
                "跳过前置配网操作"
            )

        else:
            pytest.fail(f"无法处理 SN 绑定后的页面状态: {sn_route}")

        # ---------------- 等待配网结果 ----------------

        success, error_msg = self.connecting_page.wait_for_result(
            timeout=180
        )

        if success and error_msg == "already_added":
            assert self.device_confirm_page.click_know(), \
                "关闭设备已添加提示失败"
            return

        if not success:
            if self.failure_page.is_on_failure_page():
                self.failure_page.click_retry()
                self.home_page.ensure_back_to_home()
            pytest.fail(f"设备联网失败: {error_msg}")

        assert self.device_name_page.is_on_device_name_page(), \
            "联网成功后未进入设备名称页面"
        assert self.device_name_page.input_device_name(
            config.DEVICE_NAME
        ), "输入设备名称失败"
        assert self.device_name_page.click_complete(), \
            "点击完成失败"
        time.sleep(2)

    def _wait_for_sn_wifi_route(self, timeout=20):
        """等待输入 SN 后进入 UI3、UI5 或配网结果页"""
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
        """等待 Wi-Fi 配置提交后进入 UI6、UI8 或配网结果页"""
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

    # ---------------- 蓝牙发现入口 ----------------

    def _open_bluetooth_device(self):
        assert self.home_page.open_add_device(), \
            "打开添加设备页面失败"
        assert self.add_device_page.wait_for_bluetooth_device_list(
            timeout=15
        ), "未进入发现附近设备页面"
        assert self.add_device_page.click_bluetooth_device(
            config.DEVICE_SN,
            timeout=30
        ), f"附近设备未发现目标 SN: {config.DEVICE_SN}"


    # ---------------- 扫码页手动输入 SN 入口 ----------------

    def _open_manual_sn_entry(self):
        assert self.home_page.open_scan_qr(), \
            "打开扫一扫页面失败"
        time.sleep(1)
        assert self.scan_qr_page.is_on_scan_qr_page(), \
            "未进入扫一扫页面"
        assert self.scan_qr_page.click_manual_input(), \
            "点击手动输入失败"
        time.sleep(0.5)
        assert self.manual_dialog.is_on_dialog(), \
            "手动输入弹窗未出现"
        assert self.manual_dialog.input_device_id(config.DEVICE_SN), \
            "输入设备 SN 失败"
        assert self.manual_dialog.click_confirm(), \
            "点击确定失败"
        time.sleep(1)

    # ---------------- 蓝牙 Wi-Fi 设备配网 ----------------

    def _bind_bluetooth_wifi_device(self):
        assert self.set_wifi_page.wait_for_set_wifi_page(timeout=15), \
            "选择蓝牙设备后未进入设置 Wi-Fi 页面"
        assert self.set_wifi_page.input_wifi_ssid(config.WIFI_SSID), \
            "输入 Wi-Fi 名称失败"
        assert self.set_wifi_page.input_wifi_password(config.WIFI_PASSWORD), \
            "输入 Wi-Fi 密码失败"
        assert self.set_wifi_page.click_next(), \
            "点击下一步失败"

    # ---------------- 扫码 Wi-Fi 设备配网 ----------------

    def _bind_wifi_device(self, start_page="add_device"):
        if start_page == "add_device":
            assert self.add_device_page.wait_until(
                self.add_device_page.is_on_add_device_page,
                timeout=15
            ), "SN 确认后未进入添加设备页面"
            assert self.add_device_page.check_hear_alert(True), \
                "勾选配网提示音失败"
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

        assert self.set_wifi_page.input_wifi_ssid(config.WIFI_SSID), \
            "输入路由器 Wi-Fi 名称失败"
        assert self.set_wifi_page.input_wifi_password(
            config.WIFI_PASSWORD
        ), "输入路由器 Wi-Fi 密码失败"
        assert self.set_wifi_page.click_next(), \
            "点击下一步失败"

        route = self._wait_for_wifi_next_route(timeout=20)

        if route in ("connecting", "failed", "already_added"):
            print(
                f"[BindingStress] 点击 Wi-Fi 下一步后进入页面: {route}，"
                "跳过设备热点连接"
            )
            return

        assert route == "connect_wlan", \
            f"点击下一步后页面状态异常: {route}"

        assert self.connect_wlan_page.click_connect_wlan(), \
            "点击连接设备 WLAN 失败"
        time.sleep(2)

        assert self.system_wlan_page.is_on_system_wlan_page(), \
            "未进入系统 WLAN 页面"
        assert self.system_wlan_page.connect_to_device_hotspot(
            config.DEVICE_SN
        ), f"连接设备热点 SV-{config.DEVICE_SN} 失败"

        self.driver.press("back")
        time.sleep(2)

    # ---------------- 扫码 4G 设备配网 ----------------

    def _bind_4g_device(self):
        print("[BindingStress] 4G 设备通过 SN 进入联网流程")
        time.sleep(1)

    # ---------------- Live 出图和成功截图 ----------------
    def _verify_live_preview(self):
        assert self.home_page.click_play_button(config.DEVICE_NAME), \
            f"进入设备 {config.DEVICE_NAME} 的 Live 页面失败"
        assert self.live_page.wait_for_stream_loaded(), \
            f"设备 {config.DEVICE_NAME} 绑定后未成功出图"

        print("[BindingStress] 绑定出图后停留 20 秒，再删除设备")
        time.sleep(20)

    # ---------------- 删除设备 ----------------

    def _delete_device(self):
        assert self.live_page.click_settings_gear(), \
            "进入设备设置页面失败"
        assert self.settings_page.is_on_settings_page(), \
            "未进入设备设置页面"
        assert self.settings_page.click_delete_device(), \
            "点击删除设备失败"
        assert self.settings_page.confirm_delete_dialog(confirm=True), \
            "确认删除设备失败"
        assert self.home_page.ensure_back_to_home(), \
            "删除后返回首页失败"
        assert self.home_page.refresh_device_list(), \
            "删除后刷新首页失败"
        assert self.home_page.wait_for_device_absent(config.DEVICE_NAME), \
            f"删除后首页仍存在设备: {config.DEVICE_NAME}"

    # ---------------- 失败时尽力清理 ----------------

    def _cleanup_bound_device(self):
        try:
            if not self.home_page.ensure_back_to_home():
                return

            if not self.home_page.wait_for_device(
                    config.DEVICE_NAME,
                    timeout=3
            ):
                return

            if not self.home_page.click_play_button(config.DEVICE_NAME):
                return

            if not self.live_page.click_settings_gear():
                return

            if not self.settings_page.is_on_settings_page():
                return

            if not self.settings_page.click_delete_device():
                return

            self.settings_page.confirm_delete_dialog(confirm=True)
            self.home_page.ensure_back_to_home()
            self.home_page.refresh_device_list()
        except Exception as e:
            print(f"[BindingStress] 失败后清理设备未完成: {e}")