# config.py
##################################
#           V1.1配置表            #
# 包含功能：绑定、预览、卡回看、卡录像  #
# 检索、信息校验、重启、删除          #
#            运行前请配置好         #
#                                #
##################################

# config.py
import os
import sys

# ================== 项目根目录（打包后指向 exe 所在目录） ==================
if getattr(sys, 'frozen', False):
    PROJECT_ROOT = os.path.dirname(sys.executable)
else:
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


# ----------------- 冒烟测试轮次配置 -----------------
SMOKE_ROUNDS = 200       # 冒烟的轮次
SMOKE_ROUND_INTERVAL = 10   # 下一轮需要等待的秒数


# ----------------- 测试设备参数配置 -----------------
DEVICE_NAME = "5547测"       # 设备绑定后的名称
DEVICE_SN = "5801430695547"   # 设备的sn

class SerialConfig:
    PORT = "COM3"             # 设备主控的串口
    BAUDRATE = 1500000        #串口的波特率
    TIMEOUT = 1                # 串口读取超时
    LOG_DIR = os.path.join(PROJECT_ROOT, "logs", "serial")   # 串口日志保存路径

    LOGIN_PROMPT = "login:"       # 登录提示符
    LOGIN_USERNAME = "root"       # 登录用户
    PASSWORD = "ipc&&**"          # 设备登录需要的密码
    SHELL_PROMPTS = ("# ", "#", "$ ")      # Shell 提示符列表
    REBOOT_COMMAND = "reboot"              # 重启命令
    READY_TIMEOUT = 180                 # 等待系统重启就绪超时（秒）


ADB_DEVICE_SERIAL = "RFCY108QBKM"    # 手机的序列号
PREVIEW_TIMEOUT = 30                 # 所有场景出图等待超时时间（秒）
APP_PACKAGE = "com.xc.sv360"         # APP包名
DEVICE_TYPE = "4g"                   # 设备类型：'wifi' 或 '4g'
WIFI_SSID = "TP-LINK_D130"           # 绑定的wifi名称 如果测的是wifi设备则要配置这里
WIFI_PASSWORD = "admin123"           # 绑定的wifi的密码

DEVICE_DISPLAY_NAME = "5547测"       # 信息校验的名称 需要和DEVICE_NAME = "8059测" 也就是设备绑定后的名称一致


# ----------------- 出图性能与工作模式压测配置 -----------------
# 卡回看模式轮次
WORK_MODE_TEST_ROUNDS = {
    "常电模式": 1,
    "AOV 模式": 1,
    "休眠模式": 1,
    "AOR模式": 1,
    "省电模式": 1,
    "智能模式": 1,
}

# 切换模式需要等待的时间
MODE_SWITCH_WAIT_TIME = {
    "常电模式": 5,
    "AOV 模式": 30,
    "休眠模式": 60,
    "AOR 模式": 30,
    "省电模式": 60,
    "智能模式": 30,
    "DEFAULT": 10
}

OUTPUT_RESULTS_DIR = os.path.join(PROJECT_ROOT, "outputs", "results")     # excle表保存路径


# ----------------- 设备信息校验配置 -----------------
DEVICE_MAC_ADDRESS = "2C:6F:51:49:7F:38"             # 添加后设备的mac地址
DEVICE_ICCID = "8986032442201721618"                 # 4G设备的sim卡的iccid卡号  wifi设备不用管
BATTERY_STATE_FILE = os.path.join(PROJECT_ROOT, "data", "battery_state.json")    # 电量数据保存的路径
MAX_BATTERY_DELTA = 10            # 允许的最大电量差值（%）