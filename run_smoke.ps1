# run_smoke.ps1
# 功能：读取 config.py 中的轮次配置，执行完整冒烟测试
# 用法：在项目根目录执行 .\run_smoke.ps1

# 功能：读取 config.py 的轮次配置，执行完整多轮冒烟测试
# 用法：在项目根目录运行 .\run_smoke.ps1

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$testsDir = Join-Path $projectRoot "tests"
Set-Location -LiteralPath $projectRoot

$config = & python -c "import config; print(f'{config.SMOKE_ROUNDS},{config.SMOKE_ROUND_INTERVAL}')" 2>$null

if (-not $config) {
    Write-Host "无法读取 config.py，使用默认配置：3 轮，间隔 10 秒" -ForegroundColor Yellow
    $rounds = 3
    $interval = 10
} else {
    $parts = $config -split ','
    $rounds = [int]$parts[0]
    $interval = [int]$parts[1]
}

$formatInterval = 5

$testFilesBeforeFormat = @(
    "test_add_device.py",
    "test_performance_matrix.py",
    "test_detection_recording.py",
    "test_sdcard_retrieval.py"
)

$testFilesAfterFormat = @(
    "test_device_info.py",
    "test_reboot.py",
    "test_delete.py"
)

Set-Location -LiteralPath $testsDir

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "完整冒烟测试：$rounds 轮，轮间隔 $interval 秒" -ForegroundColor Cyan
Write-Host "SD 卡每 $formatInterval 轮格式化一次" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

for ($i = 1; $i -le $rounds; $i++) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "第 $i / $rounds 轮开始" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Green

    $env:CURRENT_ROUND = "$i"
    $roundTestFiles = @($testFilesBeforeFormat)

    if (($i % $formatInterval) -eq 0) {
        $roundTestFiles += "test_sdcard_format.py"
        Write-Host "[Run] 第 $i 轮执行 SD 卡格式化" -ForegroundColor Yellow
    }

    $roundTestFiles += $testFilesAfterFormat

    & pytest @roundTestFiles -m smoke -v

    if ($LASTEXITCODE -ne 0) {
        Write-Host "`n第 $i 轮存在失败用例，继续下一轮" -ForegroundColor Yellow
    }

    if ($i -lt $rounds) {
        Write-Host "`n第 $i 轮完成，等待 $interval 秒" -ForegroundColor Cyan
        Start-Sleep -Seconds $interval
    }
}

Remove-Item Env:CURRENT_ROUND -ErrorAction SilentlyContinue

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "全部 $rounds 轮测试完成" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green