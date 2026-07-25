# locators/pairing/system_wlan_locator.py
import config

class SystemWlanLocators:
    """系统WLAN界面 (UI7) - 注意包名为 com.android.settings"""
    TITLE_WLAN = ('xpath', "//*[@text='WLAN']")
    SWITCH_BAR = ('id', 'com.android.settings:id/sesl_switchbar_text')  # "开"
    WIFI_LIST = ('id', 'com.android.settings:id/twlist')  # RecyclerView

    @staticmethod
    def get_ssid_item_locator(ssid: str):
        """根据SSID文本获取网络项"""
        # 注意：每个网络项包含title和可能summary，使用xpath精确匹配
        return ('xpath', f"//*[@resource-id='com.android.settings:id/title' and @text='{ssid}']")