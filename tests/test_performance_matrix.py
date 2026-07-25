# tests/test_performance_matrix.py
import os
import time
import pytest
import allure
import config
from datetime import datetime
from utils.result_exporter import PerformanceResultExporter
from pages.first_page.home_page import HomePage
from pages.second_page.live_page import LivePage
from pages.third_page.setting_page import SettingsPage
from pages.third_page.sdcard_replay_page import SdCardReplayPage
from pages.third_page.cloud_replay_page import CloudReplayPage
from pages.fourth_page.work_mode_page import WorkModePage


@allure.epic("IPC 自动化测试框架")
@allure.feature("全工作模式 - 出图性能综合压测")
class TestPerformanceMatrix:

    @pytest.fixture(autouse=True)
    def setup_pages(self, driver):
        self.driver = driver
        self.home_page = HomePage(driver)
        self.live_page = LivePage(driver)
        self.settings_page = SettingsPage(driver)
        self.sdcard_page = SdCardReplayPage(driver)
        self.cloud_page = CloudReplayPage(driver)
        self.work_mode_page = WorkModePage(driver)
        self.exporter = PerformanceResultExporter()

        self.home_page.ensure_back_to_home()

    # ---------------- 失败现场截图（命名规范与 conftest 完全一致）----------------
    def _attach_failure_screenshot(self, step_name: str):
        """业务层步骤失败时主动截图并挂载 Allure"""
        try:
            now_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            date_folder = datetime.now().strftime("%Y%m%d")
            save_dir = os.path.join("logs", "screenshots", date_folder)
            os.makedirs(save_dir, exist_ok=True)

            clean_name = step_name.replace("[", "_").replace("]", "_")
            file_name = f"fail_{clean_name}_{now_str}.png"
            img_path = os.path.join(save_dir, file_name)

            self.driver.screenshot(img_path)

            display_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            allure.attach.file(
                img_path,
                name=f"❌ {step_name} - 时间: {display_time}",
                attachment_type=allure.attachment_type.PNG
            )
            print(f"\n[Biz] 📸 失败截图已生成: {img_path}")
            print(f"[Biz] ⏱️ 报错精确时间点: {display_time}")
        except Exception as e:
            print(f"[Biz] ⚠️ 截图挂载失败: {e}")

    # ---------------- 业务层步骤封装（含 3 次重试）----------------
    def _run_live_step(self, device_name, max_retries=3):
        """Live 预览出图测试，失败自动重试"""
        for attempt in range(1, max_retries + 1):
            print(f"[Biz] 🎬 Live 预览出图测试 (尝试 {attempt}/{max_retries})...")
            self.home_page.ensure_back_to_home()
            self.home_page.click_play_button(device_name)

            start_t = time.time()
            success = self.live_page.wait_for_stream_loaded(timeout=config.PREVIEW_TIMEOUT)
            duration = round(time.time() - start_t, 2)

            if success:
                time.sleep(1.0)
                return True, duration

            print(f"[Biz] ⚠️ Live 预览第 {attempt}/{max_retries} 次尝试失败 (耗时 {duration}s)")
            if attempt < max_retries:
                self.driver.press("back")
                time.sleep(1.0)

        self._attach_failure_screenshot(f"Live预览失败_{device_name}")
        return False, duration

    def _run_sdcard_step(self, device_name, max_retries=3):
        """SD 卡回看出图测试，失败自动重试"""
        for attempt in range(1, max_retries + 1):
            print(f"[Biz] 💾 SD 卡回看出图测试 (尝试 {attempt}/{max_retries})...")
            self.live_page.click_card_playback()

            start_t = time.time()
            success = self.sdcard_page.wait_for_stream_loaded(timeout=config.PREVIEW_TIMEOUT)
            duration = round(time.time() - start_t, 2)

            if success:
                time.sleep(1.0)
                print("[Biz] ↩️ 从卡回看按 Back 退回 Live...")
                self.driver.press("back")
                time.sleep(1.0)
                return True, duration

            print(f"[Biz] ⚠️ SD 卡回看第 {attempt}/{max_retries} 次尝试失败 (耗时 {duration}s)")
            if attempt < max_retries:
                print("[Biz] ↩️ 退回 Live 准备重试...")
                self.driver.press("back")
                time.sleep(1.0)

        self._attach_failure_screenshot(f"SD卡回看失败_{device_name}")
        self.driver.press("back")
        time.sleep(1.0)
        return False, duration

    def _run_cloud_step(self, device_name, max_retries=3):
        """云存回看出图测试，失败自动重试"""
        for attempt in range(1, max_retries + 1):
            print(f"[Biz] ☁️ 云存回看出图测试 (尝试 {attempt}/{max_retries})...")
            self.live_page.click_cloud_playback()
            time.sleep(1.0)

            if self.cloud_page.is_on_cloud_list_page():
                print("[Biz] 🎯 当前在 UI4 列表页，点击第一个事件跳转至 UI5 播放页...")
                self.cloud_page.click_first_event_item()
            else:
                print("[Biz] ⚠️ 未能识别到 UI4 列表界面，尝试兜底二次点击...")

            start_t = time.time()
            success = self.cloud_page.wait_for_stream_loaded(timeout=config.PREVIEW_TIMEOUT)
            duration = round(time.time() - start_t, 2)

            if success:
                time.sleep(1.0)
                print("[Biz] ↩️ 退回 Live 界面...")
                self.driver.press("back")
                time.sleep(0.8)
                if not self.live_page.is_on_live_page():
                    self.driver.press("back")
                    time.sleep(0.8)
                return True, duration

            print(f"[Biz] ⚠️ 云存回看第 {attempt}/{max_retries} 次尝试失败 (耗时 {duration}s)")
            if attempt < max_retries:
                print("[Biz] ↩️ 退回 Live 准备重试...")
                self.driver.press("back")
                time.sleep(0.8)
                if not self.live_page.is_on_live_page():
                    self.driver.press("back")
                    time.sleep(0.8)

        self._attach_failure_screenshot(f"云回看失败_{device_name}")
        self.driver.press("back")
        time.sleep(0.8)
        if not self.live_page.is_on_live_page():
            self.driver.press("back")
            time.sleep(0.8)
        return False, duration

    @allure.story("动态扫描工作模式并轮询执行 Live/卡回看/云回看 出图压测")
    @pytest.mark.smoke
    def test_all_modes_preview_performance(self, serial_logger):
        device_name = getattr(config, "DEVICE_NAME", "摄像机")
        failures = []  # 收集所有失败步骤，最后统一 assert 触发 pytest FAILED

        # 1. 动态扫描模式
        self.home_page.ensure_back_to_home()
        self.home_page.click_play_button(device_name)
        self.live_page.wait_for_stream_loaded()
        time.sleep(0.5)

        self.live_page.click_settings_gear()
        time.sleep(0.5)
        self.settings_page.click_work_mode_entry()
        time.sleep(0.5)

        modes_map = self.work_mode_page.scan_device_modes()
        available_modes = list(modes_map.keys())
        print(f"[Biz] 📋 扫描到可用工作模式: {available_modes}")
        self.home_page.ensure_back_to_home()

        # 2. 模式遍历压测
        for mode in available_modes:
            rounds = config.WORK_MODE_TEST_ROUNDS.get(mode, 2)
            wait_time = config.MODE_SWITCH_WAIT_TIME.get(
                mode, config.MODE_SWITCH_WAIT_TIME.get("DEFAULT", 10)
            )

            # A. 切换工作模式
            self.home_page.ensure_back_to_home()
            time.sleep(0.5)
            self.home_page.click_play_button(device_name)
            self.live_page.wait_for_stream_loaded()
            time.sleep(0.5)

            self.live_page.click_settings_gear()
            time.sleep(0.5)
            self.settings_page.click_work_mode_entry()
            time.sleep(0.5)

            self.work_mode_page.select_mode(mode)
            time.sleep(0.5)
            self.home_page.ensure_back_to_home()

            print(f"\n[Biz] ⏳ 模式【{mode}】切换完成，回首页静置等待生效: {wait_time} 秒...")
            time.sleep(wait_time)

            # B. 压测轮次
            for r in range(1, rounds + 1):
                with allure.step(f"模式【{mode}】 - 第 {r}/{rounds} 轮压测"):
                    print(f"\n[Biz] 🔄 >>> 开始 【{mode}】 第 {r}/{rounds} 轮测试 <<<")

                    # 每轮开始前：确保设备处于休眠/待机状态（Live 冷启动唤醒的前提）
                    print(f"[Biz] 💤 第 {r} 轮开始前，回首页静置等待设备休眠: {wait_time} 秒...")
                    self.home_page.ensure_back_to_home()
                    time.sleep(wait_time)

                    # Step 1: Live 预览 (冷启动唤醒)
                    live_success, live_dur = self._run_live_step(device_name)
                    self.exporter.record_result(r, mode, "Live预览", live_dur, live_success)
                    if not live_success:
                        failures.append(f"【{mode}】第{r}轮 Live 预览失败 ({live_dur}s)")
                        self.home_page.ensure_back_to_home()
                        continue

                    # Step 2: SD 卡回看 (在 Live 页直接跳转，设备已被唤醒，无需再等休眠)
                    sd_success, sd_dur = self._run_sdcard_step(device_name)
                    self.exporter.record_result(r, mode, "SD卡回看", sd_dur, sd_success)
                    if not sd_success:
                        failures.append(f"【{mode}】第{r}轮 SD卡回看失败 ({sd_dur}s)")

                    # Step 3: 云存回看 (在 Live 页直接跳转)
                    cloud_success, cloud_dur = self._run_cloud_step(device_name)
                    self.exporter.record_result(r, mode, "云回看", cloud_dur, cloud_success)
                    if not cloud_success:
                        failures.append(f"【{mode}】第{r}轮 云回看失败 ({cloud_dur}s)")

                    # 轮次结束，回到首页
                    self.home_page.ensure_back_to_home()

        # 最后统一断言，触发 pytest FAILED 及 conftest 截图兜底
        if failures:
            fail_msg = ";\n".join(failures)
            assert False, f"出图压测存在失败项:\n{fail_msg}"











