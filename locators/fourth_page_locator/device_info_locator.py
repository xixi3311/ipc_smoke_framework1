# locators/fourth_page_locator/device_info_locator.py
import config

PKG = config.APP_PACKAGE


class DeviceInfoLocators:
    """设备信息页面定位器 (UI1: 设置页入口 / UI2: WiFi设备 / UI3: 4G设备)"""

    # ===== UI1: 设置页中的"设备信息"入口 =====
    DEVICE_INFO_ENTRY = ('id', f'{PKG}:id/deviceInfoRel')

    # ===== UI2 / UI3: 设备信息页通用定位器 =====
    # 顶部标题
    TITLE_DEVICE_INFO = ('id', f'{PKG}:id/centerText')

    # 设备名称
    DEVICE_NAME_TV = ('id', f'{PKG}:id/deviceNameTv')

    # 设备ID (SN)
    DEVICE_ID_TV = ('id', f'{PKG}:id/deviceIdTv')

    # 供电方式
    DEVICE_POWER_MODE_TV = ('id', f'{PKG}:id/devicePowerModeTv')

    # 当前电量
    DEVICE_BATTERY_TV = ('id', f'{PKG}:id/deviceElectricityLevelTv')

    # ===== UI2: WiFi设备特有定位器 =====
    # Wi-Fi网络名称
    DEVICE_WIFI_TV = ('id', f'{PKG}:id/deviceWifiTv')

    # 无线MAC地址
    DEVICE_WIFI_MAC_TV = ('id', f'{PKG}:id/deviceWiFiMACTv')

    # 有线MAC地址
    DEVICE_MAC_TV = ('id', f'{PKG}:id/deviceMACTv')

    # IP地址
    DEVICE_IP_TV = ('id', f'{PKG}:id/ipAdressTv')

    # ===== UI3: 4G设备特有定位器 =====
    # IMEI
    DEVICE_IMEI_TV = ('id', f'{PKG}:id/deviceImeiTv')

    # ICCID卡号
    DEVICE_ICCID_TV = ('id', f'{PKG}:id/deviceIccidTv')

    # 运营商
    DEVICE_OPERATOR_TV = ('id', f'{PKG}:id/deviceOperatorTv')

    # ===== 返回按钮 =====
    BTN_BACK = ('id', f'{PKG}:id/left_img')