# utils/serial_monitor.py
import os
import time
import serial
import threading
from datetime import datetime
from config import SerialConfig


class SerialMonitor:
    """
    高级串口监控与交互控制器
    日志文件命名规范参考：device_serial_YYYYMMDD_HHMMSS.log
    """

    def __init__(self, port=SerialConfig.PORT, baudrate=SerialConfig.BAUDRATE):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.is_running = False
        self.thread = None
        self.current_log_path = None
        self._lock = threading.Lock()

    # ================= 1. 日志记录与线程管理 =================
    def start_logging(self, log_name=None):
        """
        开启后台线程，持续将串口原始输出格式化写入日志文件
        :param log_name: 自定义文件名（留空则自动按 device_serial_YYYYMMDD_HHMMSS.log 生成）
        """
        os.makedirs(SerialConfig.LOG_DIR, exist_ok=True)

        # 📌 优雅的动态文件名生成逻辑（参考 OTA 脚本模式）
        if not log_name:
            time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_name = f"device_serial_{time_str}.log"

        self.current_log_path = os.path.join(SerialConfig.LOG_DIR, log_name)

        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=SerialConfig.TIMEOUT)
            self.is_running = True

            # 创建后台守护线程，避免阻塞主测试流程
            self.thread = threading.Thread(target=self._read_loop, daemon=True)
            self.thread.start()
            print(f"[Serial] 🟢 串口 {self.port} 已开启，日志写入: {self.current_log_path}")
        except Exception as e:
            print(f"[Serial Err] ❌ 串口开启失败: {e}")

    def _read_loop(self):
        """后台循环读取串口数据，带规范时间戳保存"""
        try:
            with open(self.current_log_path, "a", encoding="utf-8", errors="ignore") as f:
                while self.is_running and self.ser and self.ser.is_open:
                    try:
                        if self.ser.in_waiting:
                            raw_data = self.ser.readline()
                            if raw_data:
                                line = raw_data.decode('utf-8', errors='ignore')
                                if line.strip():  # 过滤纯空行
                                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    formatted_line = f"[{timestamp}] {line}"
                                    f.write(formatted_line)
                                    f.flush()
                        else:
                            time.sleep(0.05)  # 降低 CPU 占用
                    except Exception:
                        break
        except Exception as e:
            print(f"[Serial Err] 日志写入异常: {e}")

    def stop_logging(self):
        """停止日志抓取并安全关闭串口"""
        self.is_running = False
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
                print("[Serial] 🛑 串口连接已安全关闭")
            except Exception as e:
                print(f"[Serial Err] 关闭串口异常: {e}")

    # ================= 2. 串口控制与交互命令下发 =================
    def write_raw(self, data: str):
        """底层的串口 Raw 数据发送"""
        with self._lock:
            if self.ser and self.ser.is_open:
                self.ser.write(data.encode("utf-8"))
                self.ser.flush()

    def ensure_logged_in(self, timeout=10) -> bool:
        """自动检测并登录设备终端"""
        start_time = time.time()
        self.write_raw("\n")
        time.sleep(0.5)

        buffer = ""
        while time.time() - start_time < timeout:
            if self.ser.in_waiting:
                chunk = self.ser.read(self.ser.in_waiting).decode("utf-8", errors="ignore")
                buffer += chunk

                if any(prompt in buffer for prompt in SerialConfig.SHELL_PROMPTS):
                    return True

                if SerialConfig.LOGIN_PROMPT in buffer:
                    self.write_raw(f"{SerialConfig.LOGIN_USERNAME}\n")
                    buffer = ""
                    time.sleep(0.5)

                if "Password:" in buffer or "password:" in buffer:
                    self.write_raw(f"{SerialConfig.PASSWORD}\n")
                    buffer = ""
                    time.sleep(1.0)

            time.sleep(0.2)

        self.write_raw("\n")
        return False

    def send_cmd(self, cmd: str, timeout=5) -> str:
        """向串口发送 Shell 命令并捕获返回文本"""
        if not self.ser or not self.ser.is_open:
            print("[Serial Err] ❌ 发送命令失败，串口未连接！")
            return ""

        print(f"[Serial CMD] 🚀 执行命令: {cmd}")
        self.ensure_logged_in(timeout=3)

        with self._lock:
            self.ser.reset_input_buffer()
            self.write_raw(f"{cmd}\n")

            start_time = time.time()
            output = ""
            while time.time() - start_time < timeout:
                if self.ser.in_waiting:
                    chunk = self.ser.read(self.ser.in_waiting).decode("utf-8", errors="ignore")
                    output += chunk
                    if any(prompt in output for prompt in SerialConfig.SHELL_PROMPTS):
                        break
                time.sleep(0.1)

            return output

    def reboot_device(self, ready_timeout=SerialConfig.READY_TIMEOUT) -> bool:
        """下发 reboot 命令并等待系统再次完全就绪"""
        print("[Serial] 🔄 正在下发重启命令 reboot...")
        self.send_cmd(SerialConfig.REBOOT_COMMAND, timeout=2)

        start_time = time.time()
        time.sleep(10)
        while time.time() - start_time < ready_timeout:
            self.write_raw("\n")
            time.sleep(1)

            if os.path.exists(self.current_log_path):
                with open(self.current_log_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()[-2000:]
                    if SerialConfig.LOGIN_PROMPT in content or any(p in content for p in SerialConfig.SHELL_PROMPTS):
                        elapsed = round(time.time() - start_time, 2)
                        print(f"[Serial] 🎉 设备重启就绪完毕！耗时: {elapsed} 秒")
                        self.ensure_logged_in()
                        return True
            time.sleep(2)

        print(f"[Serial Err] ❌ 等待设备重启超时（{ready_timeout}s）！")
        return False

    def search_keyword(self, keyword: str, timeout=10) -> bool:
        """在日志文件中检索指定关键字"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if os.path.exists(self.current_log_path):
                with open(self.current_log_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if keyword in content:
                        return True
            time.sleep(1)
        return False