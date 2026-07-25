# tests/test_add_device.py
import pytest
import allure
import time
import config
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

@allure.epic("IPC 自动化测试框架")
@allure.feature("设备添加（热点绑定 - SN）")
class TestAddDevice:

    @pytest.fixture(autouse=True)
    def setup_pages(self, driver):
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

    @allure.story("热点绑定完整流程（输入SN）")
    @pytest.mark.smoke
    def test_hotspot_binding(self):
        device_sn = config.DEVICE_SN
        wifi_ssid = config.WIFI_SSID
        wifi_password = config.WIFI_PASSWORD
        device_name = config.DEVICE_DISPLAY_NAME if hasattr(config, 'DEVICE_DISPLAY_NAME') else config.DEVICE_NAME

        # 1. 首页点击扫一扫
        with allure.step("首页点击扫一扫"):
            assert self.home_page.open_scan_qr(), "打开扫一扫失败"
            time.sleep(1)

        # 2. 扫一扫页面点击手动输入
        with allure.step("点击手动输入"):
            assert self.scan_qr_page.is_on_scan_qr_page(), "未进入扫一扫页面"
            assert self.scan_qr_page.click_manual_input(), "点击手动输入失败"
            time.sleep(0.5)

        # 3. 输入设备SN并点击确定
        with allure.step(f"输入设备SN: {device_sn}"):
            assert self.manual_dialog.is_on_dialog(), "手动输入弹窗未出现"
            assert self.manual_dialog.input_device_id(device_sn), "输入设备ID失败"
            assert self.manual_dialog.click_confirm(), "点击确定失败"
            time.sleep(1)

        # 4. 添加设备页 - 勾选提示并点击热点配网
        with allure.step("勾选配网提示并点击热点配网"):
            assert self.add_device_page.is_on_add_device_page(), "未进入添加设备页"
            assert self.add_device_page.check_hear_alert(True), "勾选听提示失败"
            assert self.add_device_page.click_hotspot_pairing(), "点击热点配网失败"
            time.sleep(1)

        # 5. 设置Wi-Fi - 输入SSID和密码，点击下一步
        with allure.step(f"设置Wi-Fi: {wifi_ssid}"):
            assert self.set_wifi_page.is_on_set_wifi_page(), "未进入设置Wi-Fi页"
            assert self.set_wifi_page.input_wifi_ssid(wifi_ssid), "输入WiFi名称失败"
            assert self.set_wifi_page.input_wifi_password(wifi_password), "输入WiFi密码失败"
            assert self.set_wifi_page.click_next(), "点击下一步失败"
            time.sleep(1)

        # 6. 连接设备WLAN - 点击连接设备WLAN
        with allure.step("点击连接设备WLAN"):
            assert self.connect_wlan_page.is_on_connect_wlan_page(), "未进入连接设备WLAN页"
            assert self.connect_wlan_page.click_connect_wlan(), "点击连接设备WLAN失败"
            time.sleep(2)

        # 7. 系统WLAN - 连接设备热点
        with allure.step(f"连接热点 SV-{device_sn}"):
            assert self.system_wlan_page.is_on_system_wlan_page(), "未进入系统WLAN页面"
            assert self.system_wlan_page.connect_to_device_hotspot(device_sn), "连接热点失败"
            # 连接成功后返回App（系统会自动返回？这里手动按返回键）
            self.driver.press("back")
            time.sleep(2)

        # 8. 等待配网结果（设备联网中页面）
        with allure.step("等待配网完成（最长180秒）"):
            assert self.connecting_page.is_on_connecting_page(timeout=10), "未进入设备联网页面"
            success, error_msg = self.connecting_page.wait_for_result(timeout=180)
            if not success:
                # 如果失败，处理失败页面
                if self.failure_page.is_on_failure_page():
                    self.failure_page.click_retry()
                    self.home_page.ensure_back_to_home()
                pytest.fail(f"配网失败: {error_msg}")

        # 9. 成功：进入设备名称设置
        with allure.step(f"设置设备名称: {device_name}"):
            assert self.device_name_page.is_on_device_name_page(), "未进入设备名称设置页"
            assert self.device_name_page.input_device_name(device_name), "输入设备名称失败"
            assert self.device_name_page.click_complete(), "点击完成失败"
            time.sleep(2)

        # 10. 验证是否回到首页且设备出现在列表中
        with allure.step("验证设备已出现在首页"):
            self.home_page.ensure_back_to_home()
            device_names = self.home_page.get_current_screen_device_names()
            assert device_name in device_names, f"设备 {device_name} 未在首页列表中找到"