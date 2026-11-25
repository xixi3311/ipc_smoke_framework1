#binding_stress_config.py
#----------绑定压测---------
#       支持蓝牙、sn绑定
#-------------------------


# ----------------- 绑定压测轮次配置 -----------------
BINDING_STRESS_ROUNDS = 200      # 压测轮次
BINDING_STRESS_INTERVAL = 60     # 每一轮次间隔


# ----------------- 测试设备配置 -----------------
DEVICE_NAME = "7610测"           # 设备名称
DEVICE_SN = "5801766347610"      # 设备sn

BINDING_TYPE = "bluetooth"       # 绑定类型："bluetooth" 或 "wifi"(序列号通过序列号绑定是用这个)
DEVICE_TYPE = "wifi"             # 设备类型："4g" 或 "wifi"

WIFI_SSID = "TP-LINK_5G_D130"   # wifi名称
WIFI_PASSWORD = "a12345678"     # wifi密码

ADB_DEVICE_SERIAL = "RFCY108QBKM"   #手机序列号 adb devices得到
PREVIEW_TIMEOUT = 30                # 出图超时时间 秒


# ----------------- 串口配置 -----------------
SERIAL_PORT = "COM9"       # 串口
SERIAL_BAUDRATE = 1500000  # 波特率
SERIAL_TIMEOUT = 1