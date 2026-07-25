# verify_home_all_elements.py
import uiautomator2 as u2
import time
from datetime import datetime
import config
from pages.first_page.home_page import HomePage


def get_now_time() -> str:
    """获取当前时间字符串格式 [YYYY-MM-DD HH:MM:SS]"""
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")


def log_test(msg: str):
    """[测试] 级别的格式化日志输出"""
    print(f"{get_now_time()} [测试] {msg}")


def log_app(msg: str):
    """[App] 级别的格式化日志输出"""
    print(f"{get_now_time()} [App] {msg}")


def main():
    log_test("🚀 开始连接指定测试手机，准备验证 Home 页面 UI 元素...")
    d = u2.connect(config.ADB_DEVICE_SERIAL)
    home_page = HomePage(d)

    # 运行前确保处于首页
    log_app("检查并确保当前应用处于首页...")
    home_page.ensure_back_to_home()

    target_device = "5942AOR测"
    log_test(f"🎯 选定测试设备名称为: [{target_device}]")

    # ================= 0. 检查设备在线 / 离线状态 =================
    print("\n" + "─" * 60)
    log_test("--- 0. 检查设备在线/离线状态 ---")
    offline_info = home_page.check_device_offline_status(target_device)

    # ================= 1. 验证 ▶️ 播放按键 =================
    print("\n" + "─" * 60)
    log_test("--- 1. 验证设备画面中央 ▶️ 播放按钮击中 ---")
    if offline_info["is_offline"]:
        log_app(f"⚠️ 设备 [{target_device}] 处于离线状态 ({offline_info['offline_time']})，跳过播放测试！")
    else:
        if home_page.click_play_button(target_device):
            time.sleep(3)
            log_app(f"✅ 点击设备 [{target_device}] 播放按键成功，已进入预览界面！")
            log_app("准备退出预览返回首页...")
            home_page.ensure_back_to_home()

    # ================= 2. 验证右上角 '+' 及子菜单点击 =================
    print("\n" + "─" * 60)
    log_test("--- 2. 验证右上角 '+' 号及 '添加设备' / '扫一扫' 菜单点击 ---")

    # 2.1 点击 '添加设备'
    log_test("正在测试点击 '添加设备'...")
    if home_page.open_add_device():
        time.sleep(2)
        log_app("✅ 已成功击中并进入 '添加设备' 界面！")
        log_app("退出当前界面，准备返回首页...")
        home_page.ensure_back_to_home()

    # 2.2 点击 '扫一扫'
    log_test("正在测试点击 '扫一扫'...")
    if home_page.open_scan_qr():
        time.sleep(2)
        log_app("✅ 已成功击中并进入 '扫一扫' 界面！")
        log_app("退出当前界面，准备返回首页...")
        home_page.ensure_back_to_home()

    # ================= 3. 验证 '⋮' 竖点及 '设置' 菜单 =================
    print("\n" + "─" * 60)
    log_test("--- 3. 验证设备右下角 '⋮' 及 '设置' 菜单击中 ---")

    # 3.1 仅点击 '⋮' 竖点按钮
    if home_page.click_device_more_menu(target_device):
        time.sleep(1)

        # 3.2 校验弹出的菜单项
        settings_exist = home_page.check_more_menu_settings_exist()
        log_app(f"检查弹出菜单: '设置' 是否存在 -> {settings_exist}")

        # 3.3 点击弹出的 '设置' 选项
        if settings_exist:
            home_page.click_more_menu_settings()
            time.sleep(2)
            log_app("✅ 成功点击 '设置'，已进入设备设置界面！")
            log_app("退出设置界面，准备返回首页...")
            home_page.ensure_back_to_home()

    print("\n" + "─" * 60)
    log_test("🎉 首页所有 UI 元素交互验证完毕！")


if __name__ == "__main__":
    main()






