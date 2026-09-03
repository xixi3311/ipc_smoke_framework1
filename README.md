## 删除构建
Remove-Item -Recurse -Force build, dist, IPCAutoTest.spec 

## 打包命令
pyinstaller --onefile --console --name="IPCAutoTest" --add-data="tests;tests" --add-data="pages;pages" --add-data="locators;locators" --add-data="utils;utils" --add-data="pytest.ini;." --add-data="config.py;." --add-data="conftest.py;." --hidden-import=pytest --hidden-import=_pytest --hidden-import=pluggy --hidden-import=logging.handlers --hidden-import=allure_pytest --hidden-import=allure --hidden-import=allure_commons --hidden-import=allure_commons.logger --hidden-import=allure_commons._allure --hidden-import=allure_commons.types --hidden-import=allure_commons.utils --hidden-import=uiautomator2 --hidden-import=uiautomator2.xpath --hidden-import=serial --hidden-import=serial.tools.list_ports --hidden-import=pandas --hidden-import=openpyxl --collect-all=allure_pytest --collect-all=allure --collect-all=uiautomator2 --collect-all=pyserial --collect-all=pandas --collect-all=openpyxl run.py  

## 调试
./run_smoke.ps1

---

```markdown
# IPC 自动化冒烟测试框架

基于 **Pytest + UIAutomator2 + Allure** 的 IPC 设备自动化冒烟测试框架，采用 Page Object Model（POM）设计模式，支持 WiFi/4G 设备绑定、性能压测、卡回看检索、设备信息校验、重启/删除等核心业务场景。


## 目录结构

```
ipc_smoke_framework1/
├── config.py                 # 全局配置文件（设备信息、WiFi参数、测试轮次等）
├── conftest.py               # pytest 全局 fixtures（driver、串口日志、截图挂载）
├── pytest.ini                # pytest 运行配置
├── run_smoke.ps1             # 一键执行脚本（PowerShell）
├── run_smoke.py              # 一键执行脚本（Python）
├── requirements.txt          # Python 依赖
├── data/                     # 测试数据持久化（电量状态等）
├── locators/                 # 页面元素定位器（POM 分层）
├── pages/                    # 页面对象（POM 分层）
├── tests/                    # 测试用例
├── logs/                     # 运行日志（串口日志、截图、测试日志）
├── outputs/                  # 测试输出（性能报告 Excel）
├── reports/                  # Allure 报告数据
└── utils/                    # 工具类（日志、串口监控、结果导出）
```


## 环境要求

- Python 3.10+
- Android 设备（已开启 USB 调试）
- ADB 已配置环境变量
- 串口线（如需串口日志监控）


## 安装

```bash
# 1. 克隆项目
git clone <repository-url>
cd ipc_smoke_framework1

# 2. 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt
```

### requirements.txt

```txt
pytest>=8.0.0
uiautomator2>=3.0.0
allure-pytest>=2.0.0
pytest-repeat>=0.9.0
pandas>=2.0.0
openpyxl>=3.0.0
pyserial>=3.5.0
```


## 配置

编辑 `config.py`，根据实际设备配置以下参数：

```python
# ========== 设备参数 ==========
DEVICE_NAME = "5836测"              # 设备显示名称
DEVICE_SN = "5801911535836"         # 设备序列号
ADB_DEVICE_SERIAL = "RFCY108QBKM"   # ADB 设备序列号
APP_PACKAGE = "com.xc.sv360"        # APP 包名

# ========== 设备类型 ==========
DEVICE_TYPE = "4g"                  # "wifi" 或 "4g"

# ========== WiFi 配置（仅 WiFi 设备需要） ==========
WIFI_SSID = "360-WiFi"
WIFI_PASSWORD = "admin123"

# ========== 设备信息校验 ==========
DEVICE_MAC_ADDRESS = "2C:6F:51:3C:6B:04"
DEVICE_ICCID = "8986032442201721626"

# ========== 串口配置 ==========
class SerialConfig:
    PORT = "COM9"                   # 串口号
    BAUDRATE = 115200

# ========== 测试轮次配置 ==========
SMOKE_ROUNDS = 3                    # 冒烟测试执行轮数
SMOKE_ROUND_INTERVAL = 10           # 轮间等待时间（秒）
```


## 运行测试

### 方式一：一键执行（推荐）

```bash
# PowerShell
.\run_smoke.ps1

# 或 Python 脚本
python run_smoke.py
```

### 方式二：手动执行（单轮）

```bash
cd tests
pytest test_add_device.py test_performance_matrix.py test_sdcard_retrieval.py test_device_info.py test_reboot.py test_delete.py -m smoke -v
```

### 方式三：执行特定模块

```bash
cd tests

# 仅绑定测试
pytest test_add_device.py -m smoke -v

# 仅性能压测
pytest test_performance_matrix.py -m smoke -v

# 仅卡回看检索
pytest test_sdcard_retrieval.py -m smoke -v

# 仅设备信息校验
pytest test_device_info.py -m smoke -v

# 仅重启测试
pytest test_reboot.py -m smoke -v

# 仅删除测试
pytest test_delete.py -m smoke -v
```

### 方式四：多轮执行（Shell 循环）

```bash
# 执行 3 轮，轮间等待 10 秒
for i in {1..3}; do
    cd tests
    pytest test_add_device.py test_performance_matrix.py test_sdcard_retrieval.py test_device_info.py test_reboot.py test_delete.py -m smoke -v
    cd ..
    sleep 10
done
```


## 测试用例说明

| 测试文件 | 功能 | 标记 |
|----------|------|------|
| `test_add_device.py` | WiFi/4G 设备绑定 | `smoke` |
| `test_performance_matrix.py` | 全工作模式出图性能压测 | `smoke` |
| `test_sdcard_retrieval.py` | 卡回看事件检索与出图验证 | `smoke` |
| `test_device_info.py` | 设备信息校验（名称、ID、WiFi/MAC/ICCID、电量差值） | `smoke` |
| `test_reboot.py` | 设备重启与出图验证 | `smoke` |
| `test_delete.py` | 设备删除与解绑验证 | `smoke` / `regression` |

> ⚠️ `test_delete.py` 为破坏性操作，执行后设备将被删除，需重新绑定。建议在测试套件最后执行。


## 查看测试报告

### Allure 报告

```bash
# 生成并打开 Allure 报告
allure generate ./reports/allure-results -o ./reports/allure-report --clean
allure open ./reports/allure-report
```

### 性能数据

性能压测结果输出至 `outputs/results/preview_performance_<设备名>_<时间戳>.xlsx`

### 截图与日志

- 失败截图：`logs/screenshots/<日期>/fail_<用例名>_<时间戳>.png`
- 串口日志：`logs/serial/device_serial_<时间戳>.log`
- 测试日志：`logs/pytest_run.log`


## 电量差值校验说明

框架支持跨轮次电量差值校验：

1. **首次运行**：记录当前电量，不校验
2. **后续运行**：对比当前电量与上一轮电量
   - 差值 ≤ 10%：通过，更新电量记录
   - 差值 > 10%：失败
3. **数据过期**：超过 2 小时未更新，视为失效，重新记录

电量数据存储：`data/battery_state.json`

```json
{
    "5801911535836": {
        "last_battery": 50,
        "last_update": "2026-09-01 10:30:00"
    }
}
```


## 常见问题

### 1. 串口打开失败

```
[Serial Err] ❌ 串口开启失败: could not open port 'COM4'
```

**解决方案**：
- 检查 `config.py` 中 `SerialConfig.PORT` 是否为实际串口号
- 如不需要串口日志，可忽略此警告

### 2. 首页判断不准确

**解决方案**：
- `is_on_home_page()` 使用宽松判断（底部"设备"Tab 选中 / "所有设备"标题 / 加号按钮）
- 如加号按钮 ID 变化，更新 `HomeLocators.Home_TOP_PLUS_BTN`

### 3. 4G 设备绑定过快导致 UI8 检测失败

**解决方案**：
- `wait_for_result()` 同时检测 UI8/UI9/UI10 三种状态
- 已自动处理，无需额外配置

### 4. 电量数据跨轮次不准确

**解决方案**：
- 电量数据以 `DEVICE_SN` 为 key 存储，自动绑定设备
- 超过 2 小时自动失效，重新记录


## 扩展开发

### 新增测试用例

1. 在 `tests/` 下新建 `test_xxx.py`
2. 使用 `@pytest.mark.smoke` 标记
3. 继承 POM 页面对象
4. 编写测试步骤

### 新增页面对象

1. 在 `locators/` 下新建定位器文件
2. 在 `pages/` 下新建页面类
3. 继承 `BasePage`
4. 实现业务方法


## 维护者

- 自动化测试团队


## 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-09-01 | v1.0 | 初始版本：绑定、性能、卡回看、设备信息、重启、删除 |
```



