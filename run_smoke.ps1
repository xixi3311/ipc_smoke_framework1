# run_smoke.ps1
# 功能：读取 config.py 中的轮次配置，执行完整冒烟测试
# 用法：在项目根目录执行 .\run_smoke.ps1

# 切换到 tests 目录
Set-Location -Path "tests"

# 从 config.py 读取配置（通过 Python 输出）
$config = python -c "import sys; sys.path.insert(0, '.'); import config; print(f'{config.SMOKE_ROUNDS},{config.SMOKE_ROUND_INTERVAL}')" 2>$null

if (-not $config) {
    Write-Host "WARNING: Cannot read config.py, using defaults: rounds=3, interval=10s" -ForegroundColor Yellow
    $rounds = 3
    $interval = 10
} else {
    $parts = $config -split ','
    $rounds = [int]$parts[0]
    $interval = [int]$parts[1]
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Full Smoke Test - $rounds rounds, interval $interval seconds" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$testFiles = @(
    "test_add_device.py",
    "test_performance_matrix.py",
    "test_sdcard_retrieval.py",
    "test_device_info.py",
    "test_reboot.py",
    "test_delete.py"
)

for ($i=1; $i -le $rounds; $i++) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "  Round $i / $rounds start" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Green

    pytest $testFiles -m smoke -v

    if ($LASTEXITCODE -ne 0) {
        Write-Host "`nWARNING: Round $i has failures, continuing..." -ForegroundColor Yellow
    }

    if ($i -lt $rounds) {
        Write-Host "`n===== Round $i completed, waiting $interval seconds for next round =====" -ForegroundColor Cyan
        Start-Sleep -Seconds $interval
    }
}

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "  All $rounds rounds completed!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green