# IPC 自动化测试框架

基于 Pytest、uiautomator2 和 Allure 的 IPC 设备自动化测试框架，使用 Page Object Model（POM）组织页面与元素定位。

当前全量轮次流程：

1. 绑定设备。
2. 执行工作模式性能矩阵。
3. 开启画面翻转和车型侦测，在预览中持续触发侦测 1 分钟。
4. 检索并回放 SD 卡中的侦测录像。
5. 第 5、10、15……轮在卡回看之后格式化 SD 卡。
6. 校验设备信息。
7. 重启设备。
8. 删除设备，结束本轮。

格式化会删除 SD 卡上的录像和其他文件。格式化用例每 5 轮执行一次，失败后不重试；测试会尝试返回首页。

## 运行入口说明

打包和未打包运行使用不同入口，选择其中一种运行即可：

| 场景 | 入口 | 说明 |
|---|---|---|
| PyInstaller 打包后的 EXE | `run.py` | PyInstaller 命令的目标文件是 `run.py`。EXE 内部由它按配置循环执行测试。 |
| 未打包的 Python 多轮运行 | `loop_run.py` | 使用当前 Python 环境直接运行多轮测试。它不依赖 `run.py`。 |
| 未打包的 PowerShell 多轮运行 | `run_smoke.ps1` | 通过 PowerShell 调用 pytest 多轮运行。它不依赖 `run.py` 或 `loop_run.py`。 |
| 单独调试一个用例 | `pytest` | 直接指定测试文件，不经过以上多轮 runner。 |

EXE 只依赖 `run.py`。`loop_run.py` 和 `run_smoke.ps1` 是本地直接运行的替代入口，不会被 EXE 调用。三个多轮入口应保持相同的流程顺序和每 5 轮格式化规则。

## 目录结构

```text
ipc_smoke_framework1/
├── config.py
├── conftest.py
├── pytest.ini
├── run.py
├── loop_run.py
├── run_smoke.ps1
├── requirements.txt
├── data/
├── locators/
├── pages/
├── tests/
├── logs/
├── outputs/
├── reports/
└── utils/
```

## 环境准备

- Windows 测试电脑和 Android 测试手机。
- Python、pytest 和 `requirements.txt` 中的依赖。
- ADB 已安装并配置到 `PATH`，手机已开启 USB 调试。
- 如果需要设备串口日志，连接配置的 COM 串口并确保没有其他程序占用。
- 用于触发人形、车型侦测的视频应在电脑上持续播放。

安装依赖：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

确认手机连接：

```powershell
adb devices
```

## 配置

运行前检查 `config.py` 中的设备名称、序列号、轮次、手机 ADB 序列号和串口配置：

```python
SMOKE_ROUNDS = 200
SMOKE_ROUND_INTERVAL = 10

DEVICE_NAME = "设备名称"
DEVICE_SN = "设备序列号"
ADB_DEVICE_SERIAL = "手机ADB序列号"
APP_PACKAGE = "com.xc.sv360"

class SerialConfig:
    PORT = "COM9"
    BAUDRATE = 1500000
```

`SMOKE_ROUNDS` 是全量运行轮数，`SMOKE_ROUND_INTERVAL` 是轮间等待秒数。格式化发生在轮数能被 5 整除的轮次，并且排在卡回看之后、设备信息校验之前。

## 未打包运行

在项目根目录选择一种多轮入口运行。

PowerShell：

```powershell
python -u .\run.py     #调试
```

Python：

```powershell
python loop_run.py
```

不要同时启动两个多轮入口，否则它们会同时操作同一台手机和设备。

### 单独调试

在项目根目录运行指定用例：

```powershell
pytest tests/test_detection_recording.py -m smoke -v -s
pytest tests/test_sdcard_retrieval.py -m smoke -v -s
pytest tests/test_sdcard_format.py -m smoke -v -s
```

`test_sdcard_format.py` 会实际格式化 SD 卡并删除卡内文件。单独调试前请确认卡内没有需要保留的数据。

## PyInstaller 打包与运行

在项目根目录执行以下命令。`--add-data="tests;tests"` 会将测试目录打入 EXE，测试执行顺序由 `run.py` 中的测试清单控制。

```powershell
pyinstaller --onefile --console --name="IPCAutoTest" `
  --add-data="tests;tests" --add-data="pages;pages" `
  --add-data="locators;locators" --add-data="utils;utils" `
  --add-data="pytest.ini;." --add-data="config.py;." `
  --add-data="conftest.py;." `
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
  run.py
```

生成文件位于 `dist\IPCAutoTest.exe`。将 EXE 放在需要保存 `config.py` 配置、日志、报告和结果文件的目录中运行；打包模式下运行数据目录相对 EXE 所在目录创建。

打包前清理旧构建产物（可选）：

```powershell
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force IPCAutoTest.spec -ErrorAction SilentlyContinue
```

## 测试用例

| 文件 | 用途 | 全量运行频率 |
|---|---|---|
| `test_add_device.py` | 绑定设备 | 每轮 |
| `test_performance_matrix.py` | 工作模式与预览性能矩阵 | 每轮 |
| `test_detection_recording.py` | 确保翻转和车型侦测开启，预览触发 1 分钟 | 每轮 |
| `test_sdcard_retrieval.py` | 检索和回放人形、车型卡录像 | 每轮 |
| `test_sdcard_format.py` | 检查 SD 卡并格式化 | 每 5 轮 |
| `test_device_info.py` | 校验设备信息 | 每轮 |
| `test_reboot.py` | 重启设备验证 | 每轮 |
| `test_delete.py` | 删除设备 | 每轮，作为轮次最后步骤 |

调试用例 `test_enable_detection.py` 用于单独验证车型侦测开关，不列入全量运行清单。

## 输出文件

- Excel 测试结果：`outputs/results/test_report_<设备名称>.xlsx`
- 运行汇总日志：`logs/run_output.log`
- Pytest 日志：`logs/pytest_run.log`
- 串口日志：`logs/serial/`
- 失败截图：`logs/screenshots/<日期>/`
- Allure 原始数据：`reports/allure-results/`

若安装了 Allure 命令行工具，可生成 HTML 报告：

```powershell
allure generate .\reports\allure-results -o .\reports\allure-report --clean
allure open .\reports\allure-report
```

## 常见问题

### 串口提示拒绝访问

检查 `config.py` 中的 `SerialConfig.PORT`，并关闭占用该串口的终端或串口工具。串口日志启动失败不会自动说明 UI 测试已失败，但会缺少串口采集结果。

### 找不到设备或无法连接 App

检查 `ADB_DEVICE_SERIAL`、USB 调试授权和 `adb devices` 输出；确认测试设备已绑定并显示在 App 首页。

### SD 卡未接入或格式化失败

格式化用例要求设备识别到 SD 卡。未接入会使该用例失败；格式化失败时点击取消，不自动重试。卡格式化会删除已存文件。

### Excel 轮次显示不正确

`run.py`、`loop_run.py` 和 `run_smoke.ps1` 在每轮执行前设置 `CURRENT_ROUND`，`conftest.py` 使用它写入当前轮次。
