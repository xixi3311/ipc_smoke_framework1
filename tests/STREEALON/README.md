当前项目里还没有 standalone/binding_stress/README.md；`tests/STREEALON/README.md` 还是旧流程，写着 BINDING_TYPE=wifi。下面是按当前 runner 和压测用例整理的完整 README，可直接保存为 standalone/binding_stress/README.md。
# 绑定压测

独立运行设备绑定、Live 出图和删除流程。压测入口是 `binding_stress_runner.py`，每次启动会按配置连续执行多轮。

## 单轮流程

1. 按配置使用蓝牙或 SN 入口绑定设备。
2. 等待设备联网，并完成设备名称设置。
3. 回到首页刷新设备列表，进入 Live 预览并等待出图。
4. 出图后停留 20 秒。
5. 删除刚绑定的设备。

绑定、出图或删除步骤失败时，本轮记为失败；runner 会按配置继续后续轮次。测试失败时会保存失败截图。

## 绑定方式

`BINDING_TYPE` 和 `DEVICE_TYPE` 控制绑定入口及设备联网方式：

| `BINDING_TYPE` | `DEVICE_TYPE` | 流程 |
|---|---|---|
| `bluetooth` | `wifi` | 发现附近蓝牙设备 → 设置路由器 Wi-Fi → 设备联网 |
| `sn` | `wifi` | 手动输入 SN → 设置路由器 Wi-Fi → 设备联网 |
| `sn` | `4g` | 手动输入 SN → 等待 4G 设备联网 |

Wi-Fi 设备使用 SN 绑定时，App 可能记住之前的配网流程：

- 常规流程：输入 SN 后进入添加设备页，确认听到提示音并选择热点配网，然后设置路由器 Wi-Fi。
- 已记忆流程：输入 SN 后直接进入设置 Wi-Fi 页面，跳过添加设备页和设备热点连接步骤。

压测会根据实际出现的页面继续对应流程。

当前不支持 `BINDING_TYPE="bluetooth"` 与 `DEVICE_TYPE="4g"` 的组合。

## 修改配置

打包后，在 `IPCABindingStress.exe` 同目录编辑 `binding_stress_config.py`。Runner 会优先读取这个外部配置文件。

```python
BINDING_STRESS_ROUNDS = 200
BINDING_STRESS_INTERVAL = 60

DEVICE_NAME = "7610测"
DEVICE_SN = "5801766347610"

BINDING_TYPE = "bluetooth"  # "sn" 或 "bluetooth"
DEVICE_TYPE = "wifi"        # "wifi" 或 "4g"

WIFI_SSID = "TP-LINK_5G_D130"
WIFI_PASSWORD = "a12345678"

ADB_DEVICE_SERIAL = "RFCY108QBKM"
PREVIEW_TIMEOUT = 30

SERIAL_PORT = "COM9"
SERIAL_BAUDRATE = 1500000
SERIAL_TIMEOUT = 1
配置说明：
- BINDING_STRESS_ROUNDS：总轮数。
- BINDING_STRESS_INTERVAL：每轮结束后、下一轮开始前等待的秒数。
- DEVICE_NAME：绑定后设置的设备名称。
- DEVICE_SN：设备 SN。
- BINDING_TYPE：`sn` 或 bluetooth。
- DEVICE_TYPE：设备类型，`wifi` 或 4g。
- WIFI_SSID、`WIFI_PASSWORD`：Wi-Fi 设备使用的路由器名称和密码。
- ADB_DEVICE_SERIAL：连接测试手机的 ADB 序列号。
- PREVIEW_TIMEOUT：等待 Live 出图的最长时间，单位为秒。
- SERIAL_PORT、`SERIAL_BAUDRATE`、`SERIAL_TIMEOUT`：设备串口参数。
输出文件
每次启动 runner 都会生成独立的运行日志和 Excel 结果；压测轮次不会各自创建一份 Excel。
运行目录/
├─ IPCABindingStress.exe
├─ binding_stress_config.py
├─ logs/
│  └─ binding_stress/
│     ├─ binding_stress_run_<启动时间>.log
│     ├─ binding_stress_pytest_<启动时间>.log
│     ├─ serial/
│     │  └─ device_serial_<启动时间>.log
│     └─ screenshots/
│        └─ <日期>/
│           └─ 失败截图
├─ outputs/
│  └─ binding_stress/
│     └─ test_report_<设备名称>_<启动时间>.xlsx
└─ reports/
   └─ binding_stress/
      └─ <启动时间>/
         └─ allure-results/
- binding_stress_run_*.log：本次压测的完整控制台日志，包含所有轮次。
- binding_stress_pytest_*.log：本次运行的 Pytest 日志。
- serial/：本次压测共用的串口日志；串口在整场压测启动时打开，结束时关闭。
- screenshots/：测试失败时生成的截图，不会因成功出图而逐轮保存截图。
- test_report_*.xlsx：本次压测的轮次结果。
- allure-results/：本次压测所有轮次的 Allure 原始结果；每次重新启动 runner 会使用新的目录。
打包
在项目根目录打开 PowerShell，执行以下命令：
pyinstaller --onefile --console --name="IPCABindingStress" `
  --distpath="standalone\binding_stress\dist" `
  --workpath="standalone\binding_stress\build" `
  --specpath="standalone\binding_stress" `
  --add-data="..\..\tests;tests" `
  --add-data="..\..\pages;pages" `
  --add-data="..\..\locators;locators" `
  --add-data="..\..\utils;utils" `
  --add-data="..\..\pytest.ini;." `
  --add-data="..\..\config.py;." `
  --add-data="..\..\conftest.py;." `
  --add-data="binding_stress_config.py;." `
  --hidden-import=pytest --hidden-import=_pytest --hidden-import=pluggy `
  --hidden-import=logging.handlers --hidden-import=allure_pytest `
  --hidden-import=allure --hidden-import=allure_commons `
  --hidden-import=allure_commons.logger --hidden-import=allure_commons._allure `
  --hidden-import=allure_commons.types --hidden-import=allure_commons.utils `
  --hidden-import=uiautomator2 --hidden-import=uiautomator2.xpath `
  --hidden-import=serial --hidden-import=serial.tools.list_ports `
  --hidden-import=pandas --hidden-import=openpyxl `
  --collect-all=allure_pytest --collect-all=allure `
  --collect-all=uiautomator2 --collect-all=pyserial `
  --collect-all=pandas --collect-all=openpyxl `
  standalone\binding_stress\binding_stress_runner.py
打包完成后，将 standalone\binding_stress\dist\IPCABindingStress.exe 和最新的 binding_stress_config.py 放到同一个新建目录。之后修改压测参数只需编辑这个目录里的配置文件，不需要重新打包。
清理旧打包文件
需要重新打包且希望清除上次构建产物时，在项目根目录执行：
Remove-Item -Recurse -Force `
  .\standalone\binding_stress\build, `
  .\standalone\binding_stress\dist `
  -ErrorAction SilentlyContinue

Remove-Item -Force `
  .\standalone\binding_stress\IPCABindingStress.spec `
  -ErrorAction SilentlyContinue

