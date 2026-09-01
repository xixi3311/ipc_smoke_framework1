# config.py

# ----------------- 冒烟测试轮次配置 -----------------
# 完整冒烟测试执行轮数
SMOKE_ROUNDS = 2

# 每轮之间的等待时间（秒）
SMOKE_ROUND_INTERVAL = 10

# ----------------- 测试设备参数配置 -----------------
# APP 首页展示的设备名称（用于精准定位和点击卡片，例如 "5556测AOV"）
DEVICE_NAME = "5836测"

# 设备序列号 / sn（如 5801703758022）
DEVICE_SN = "5801911535836"

class SerialConfig:
    PORT = "COM9"  # 串口号（如 COM8 或 /dev/ttyUSB0）
    BAUDRATE = 1500000  # IPC 串口波特率
    TIMEOUT = 1  # 串口读取超时
    LOG_DIR = "logs/serial"  # 串口日志存放目录

    # 交互控制配置（移植自 OTA 脚本）
    LOGIN_PROMPT = "login:"  # 登录提示符
    LOGIN_USERNAME = "root"  # 登录用户名
    PASSWORD = ""  # 登录密码
    SHELL_PROMPTS = ("# ", "#", "$ ")  # Shell 提示符列表
    REBOOT_COMMAND = "reboot"  # 重启命令
    READY_TIMEOUT = 180  # 等待系统重启就绪超时（秒）


# 如果是通过 USB 连接单台设备，可以直接留空字符串 "" 或 "127.0.0.1:5555"
ADB_DEVICE_SERIAL = "RFCY108QBKM"

# 所有场景出图等待超时时间（秒）
PREVIEW_TIMEOUT = 30


# APP包名
APP_PACKAGE = "com.xc.sv360"

# ----------------- 设备绑定配置 -----------------
# 设备类型：'wifi' 或 '4g'
DEVICE_TYPE = "4g"  # 或 "4g"

# ----------------- 设备配网（热点绑定）配置 -----------------
WIFI_SSID = "TP-LINK_D130"                 # 路由器WiFi名称（请修改为实际SSID）
WIFI_PASSWORD = "admin123"          # 路由器WiFi密码

#设备添加之后的名字
DEVICE_DISPLAY_NAME = "5836测"     # 绑定后显示的设备名称（可与DEVICE_NAME相同）


# ----------------- 出图性能与工作模式压测配置 -----------------
# 各工作模式下的压测轮次配置
WORK_MODE_TEST_ROUNDS = {
    "常电模式": 1,      # 常电模式跑 4 轮
    "AOV 模式": 1,      # AOV 模式跑 3 轮
    "休眠模式": 1,      # 休眠模式跑 2 轮
    "AOR模式": 1,     # AOR模式
    "省电模式": 1,     # 省电模式
    "智能模式": 1,     # 智能模式
}

# 模式切换后的静置等待时间（秒），确保设备真正进入对应状态（特别休眠模式）
MODE_SWITCH_WAIT_TIME = {
    "常电模式": 5,
    "AOV 模式": 30,
    "休眠模式": 60,     # 休眠模式强制静置 60 秒等待进入深度休眠
    "AOR 模式": 30,
    "省电模式": 60,      # 省电模式
    "智能模式": 30,       # 智能模式
    "DEFAULT": 10      # 默认等待时间
}

# 结果 Excel 导出目录
OUTPUT_RESULTS_DIR = "outputs/results"

# ----------------- 设备信息校验配置 -----------------
# WiFi 设备有线 MAC 地址
DEVICE_MAC_ADDRESS = "2C:6F:51:4A:10:5F"

# 4G 设备 ICCID 卡号
DEVICE_ICCID = "8986032442201721626"

# 电量保存文件路径
BATTERY_STATE_FILE = "data/battery_state.json"

# 允许的最大电量差值（%）
MAX_BATTERY_DELTA = 10