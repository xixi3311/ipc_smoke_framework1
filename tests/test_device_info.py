# tests/test_device_info.py
import pytest
import allure
import time
import config
from pages.first_page.home_page import HomePage
from pages.second_page.live_page import LivePage
from pages.third_page.setting_page import SettingsPage
from pages.fourth_page.device_info_page import DeviceInfoPage


@allure.epic("IPC 自动化测试框架")
@allure.feature("设备信息校验")
class TestDeviceInfo:

    TARGET_DEVICE = getattr(config, "DEVICE_NAME", "摄像机")
    DEVICE_SN = getattr(config, "DEVICE_SN", "")
    DEVICE_MAC = getattr(config, "DEVICE_MAC_ADDRESS", "")
    DEVICE_ICCID = getattr(config, "DEVICE_ICCID", "")
    WIFI_SSID = getattr(config, "WIFI_SSID", "")

    @pytest.fixture(autouse=True)
    def setup_pages(self, driver):
        self.driver = driver
        self.home_page = HomePage(driver)
        self.live_page = LivePage(driver)
        self.settings_page = SettingsPage(driver)
        self.device_info_page = DeviceInfoPage(driver)
        # 确保回到首页
        self.home_page.ensure_back_to_home()

    def _enter_device_info_page(self) -> bool:
        """公共步骤：进入设备信息页"""
        # 1. 进入 Live
        self.home_page.click_play_button(self.TARGET_DEVICE)
        self.live_page.wait_for_stream_loaded()

        # 2. 进入设置
        self.live_page.click_settings_gear()
        assert self.settings_page.is_on_settings_page(), "未能进入设置页"

        # 3. 进入设备信息
        assert self.device_info_page.enter_device_info(), "点击'设备信息'入口失败"
        assert self.device_info_page.is_on_device_info_page(), "未能进入设备信息页"
        return True

    def _verify_common_fields(self, info: dict) -> None:
        """校验设备名称和 ID"""
        # 设备名称校验
        expected_name = self.TARGET_DEVICE
        actual_name = info.get("device_name", "")
        assert actual_name == expected_name, \
            f"设备名称不匹配: 期望 '{expected_name}'，实际 '{actual_name}'"

        # 设备 ID (SN) 校验
        expected_sn = self.DEVICE_SN
        actual_sn = info.get("device_id", "")
        assert actual_sn == expected_sn, \
            f"设备ID不匹配: 期望 '{expected_sn}'，实际 '{actual_sn}'"

    @allure.story("WiFi 设备信息校验")
    @pytest.mark.smoke
    def test_wifi_device_info_verification(self):
        """校验 WiFi 设备的：名称、ID、WiFi网络、MAC地址、电量差值"""
        # 1. 进入设备信息页
        self._enter_device_info_page()

        # 2. 判断设备类型
        device_type = self.device_info_page.get_device_type()
        if device_type != "wifi":
            pytest.skip(f"当前设备是 4G 设备 (实际类型: {device_type})，跳过 WiFi 校验")

        # 3. 获取 WiFi 设备信息
        info = self.device_info_page.get_wifi_device_info()

        # 4. 校验基本信息
        with allure.step("校验设备名称和ID"):
            self._verify_common_fields(info)

        with allure.step(f"校验 WiFi 网络: 期望 '{self.WIFI_SSID}'"):
            actual_wifi = info.get("wifi_network", "")
            assert actual_wifi == self.WIFI_SSID, \
                f"WiFi网络不匹配: 期望 '{self.WIFI_SSID}'，实际 '{actual_wifi}'"

        with allure.step(f"校验有线MAC地址: 期望 '{self.DEVICE_MAC}'"):
            actual_mac = info.get("mac_address", "")
            assert actual_mac == self.DEVICE_MAC, \
                f"有线MAC地址不匹配: 期望 '{self.DEVICE_MAC}'，实际 '{actual_mac}'"

        # 5. 电量差值校验
        with allure.step(f"校验电量差值 ≤ {config.MAX_BATTERY_DELTA}%"):
            current_battery = info.get("battery", -1)
            if current_battery < 0:
                allure.attach("当前电量获取失败，跳过差值校验", name="电量校验警告")
                pytest.skip("当前电量获取失败，跳过差值校验")

            passed, delta, last_battery = self.device_info_page.verify_battery_delta(
                current_battery, self.DEVICE_SN
            )
            assert passed, f"电量差值 {delta}% 超过阈值 {config.MAX_BATTERY_DELTA}%"

            # 附加 Allure 信息
            allure.attach(
                f"当前电量: {current_battery}%\n上一轮电量: {last_battery}%\n差值: {delta}%\n阈值: {config.MAX_BATTERY_DELTA}%",
                name="电量校验详情",
                attachment_type=allure.attachment_type.TEXT
            )

        # 6. 返回首页
        with allure.step("返回首页"):
            self.device_info_page.click_back_to_live()
            self.live_page.click_back_to_home()
            self.home_page.ensure_back_to_home()

    @allure.story("4G 设备信息校验")
    @pytest.mark.smoke
    def test_4g_device_info_verification(self):
        """校验 4G 设备的：名称、ID、ICCID、电量差值"""
        # 1. 进入设备信息页
        self._enter_device_info_page()

        # 2. 判断设备类型
        device_type = self.device_info_page.get_device_type()
        if device_type != "4g":
            pytest.skip(f"当前设备是 WiFi 设备 (实际类型: {device_type})，跳过 4G 校验")

        # 3. 获取 4G 设备信息
        info = self.device_info_page.get_4g_device_info()

        # 4. 校验基本信息
        with allure.step("校验设备名称和ID"):
            self._verify_common_fields(info)

        with allure.step(f"校验 ICCID: 期望 '{self.DEVICE_ICCID}'"):
            actual_iccid = info.get("iccid", "")
            assert actual_iccid == self.DEVICE_ICCID, \
                f"ICCID不匹配: 期望 '{self.DEVICE_ICCID}'，实际 '{actual_iccid}'"

        # 5. 电量差值校验
        with allure.step(f"校验电量差值 ≤ {config.MAX_BATTERY_DELTA}%"):
            current_battery = info.get("battery", -1)
            if current_battery < 0:
                allure.attach("当前电量获取失败，跳过差值校验", name="电量校验警告")
                pytest.skip("当前电量获取失败，跳过差值校验")

            passed, delta, last_battery = self.device_info_page.verify_battery_delta(
                current_battery, self.DEVICE_SN
            )
            assert passed, f"电量差值 {delta}% 超过阈值 {config.MAX_BATTERY_DELTA}%"

            allure.attach(
                f"当前电量: {current_battery}%\n上一轮电量: {last_battery}%\n差值: {delta}%\n阈值: {config.MAX_BATTERY_DELTA}%",
                name="电量校验详情",
                attachment_type=allure.attachment_type.TEXT
            )

        # 6. 返回首页
        with allure.step("返回首页"):
            self.device_info_page.click_back_to_live()
            self.live_page.click_back_to_home()
            self.home_page.ensure_back_to_home()