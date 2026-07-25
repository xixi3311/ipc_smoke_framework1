# utils/result_exporter.py
import os
import pandas as pd
from datetime import datetime
import config


class PerformanceResultExporter:
    """出图性能压测结果导出器（生成 Excel 汇总）"""

    def __init__(self):
        os.makedirs(config.OUTPUT_RESULTS_DIR, exist_ok=True)
        time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.excel_path = os.path.join(
            config.OUTPUT_RESULTS_DIR,
            f"preview_performance_{config.DEVICE_NAME}_{time_str}.xlsx"
        )
        self.records = []

    def record_result(self, round_num: int, mode: str, biz_type: str, duration: float, success: bool, remark: str = ""):
        """记录单次测试数据"""
        data = {
            "设备名称": config.DEVICE_NAME,
            "设备 SN": config.DEVICE_SN,
            "测试轮次": f"第 {round_num} 轮",
            "工作模式": mode,
            "业务类型": biz_type,
            "出图耗时(秒)": round(duration, 2) if success else "TIMEOUT/FAIL",
            "测试结果": "PASS" if success else "FAIL",
            "记录时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "备注信息": remark
        }
        self.records.append(data)
        self.save_to_excel()

    def save_to_excel(self):
        """实时刷新保存到 Excel 表格"""
        try:
            df = pd.DataFrame(self.records)
            df.to_excel(self.excel_path, index=False, engine='openpyxl')
            print(f"[Exporter] 📊 性能数据已实时同步至: {self.excel_path}")
        except Exception as e:
            print(f"[Exporter Err] ❌ 保存 Excel 失败: {e}")