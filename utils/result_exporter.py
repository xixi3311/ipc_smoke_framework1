# utils/result_exporter.py
import os
import pandas as pd
from datetime import datetime
import config


class PerformanceResultExporter:
    """全量测试结果导出器（支持多轮次追加）"""

    def __init__(self):
        os.makedirs(config.OUTPUT_RESULTS_DIR, exist_ok=True)
        # 固定文件名，所有轮次追加到同一个文件
        self.excel_path = os.path.join(
            config.OUTPUT_RESULTS_DIR,
            f"test_report_{config.DEVICE_NAME}.xlsx"
        )
        self.records = []
        self.errors = []
        self._load_existing()

    def _load_existing(self):
        """读取已有数据，支持追加"""
        if os.path.exists(self.excel_path):
            try:
                df = pd.read_excel(self.excel_path, sheet_name='测试明细')
                self.records = df.to_dict('records')
                # 把图标还原回文本，避免重复映射
                for r in self.records:
                    val = r.get('测试结果', '')
                    if val == '✅':
                        r['测试结果'] = 'PASS'
                    elif val == '❌':
                        r['测试结果'] = 'FAIL'
                    elif val == '⏭️':
                        r['测试结果'] = 'SKIP'
            except Exception:
                pass

    def record_result(self, round_num: int, test_type: str, mode: str,
                      biz_type: str, duration: float, success: bool, remark: str = ""):
        # 截断备注，避免 Excel 单元格过长
        remark = str(remark)[:120] if remark else ""

        data = {
            "设备名称": config.DEVICE_NAME,
            "设备 SN": str(config.DEVICE_SN),  # 强制字符串，避免科学计数法
            "测试轮次": f"第 {round_num} 轮",
            "测试类型": test_type,
            "工作模式": mode if mode else "-",
            "业务类型": biz_type,
            "耗时(秒)": round(duration, 2) if duration else "N/A",
            "测试结果": "PASS" if success else "FAIL",
            "记录时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "备注": remark
        }
        self.records.append(data)
        self.save_to_excel()

    def record_error(self, round_num: int, test_type: str, test_case: str, error_msg: str):
        error_msg = str(error_msg)[:200]
        self.errors.append({
            "测试轮次": f"第 {round_num} 轮",
            "测试类型": test_type,
            "用例名称": test_case,
            "错误信息": error_msg,
            "发生时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self.save_to_excel()

    def save_to_excel(self):
        try:
            with pd.ExcelWriter(self.excel_path, engine='openpyxl') as writer:
                # Sheet1: 测试明细
                if self.records:
                    df = pd.DataFrame(self.records)
                    # 避免 SN 科学计数法
                    df['设备 SN'] = df['设备 SN'].astype(str)
                    # PASS/FAIL 换成图标（更直观）
                    df['测试结果'] = df['测试结果'].map({
                        'PASS': '✅',
                        'FAIL': '❌',
                        'SKIP': '⏭️'
                    })
                    df.to_excel(writer, sheet_name='测试明细', index=False)
                    self._adjust_column_width(writer.sheets['测试明细'])

                # Sheet2: 汇总统计
                summary = self._build_summary()
                df_summary = pd.DataFrame(summary)
                df_summary.to_excel(writer, sheet_name='汇总统计', index=False)
                self._adjust_column_width(writer.sheets['汇总统计'])

                # Sheet3: 错误详情
                if self.errors:
                    df_errors = pd.DataFrame(self.errors)
                    df_errors.to_excel(writer, sheet_name='错误详情', index=False)
                    self._adjust_column_width(writer.sheets['错误详情'])

            print(f"[Exporter]  数据已同步至: {self.excel_path}")
        except Exception as e:
            print(f"[Exporter Err] ❌ 保存 Excel 失败: {e}")

    def _adjust_column_width(self, worksheet):
        """自动调整列宽"""
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    length = len(str(cell.value))
                    if length > max_length:
                        max_length = length
                except:
                    pass
            # 最大宽度限制 50，避免太宽
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

    def _build_summary(self):
        total = len(self.records)
        passed = sum(1 for r in self.records if r.get("测试结果") == "PASS")
        failed = total - passed
        success_rate = f"{(passed / total * 100):.1f}%" if total > 0 else "N/A"

        summary = [
            {"统计项": "设备名称", "值": config.DEVICE_NAME},
            {"统计项": "设备 SN", "值": str(config.DEVICE_SN)},
            {"统计项": "总记录数", "值": total},
            {"统计项": "✅ PASS", "值": passed},
            {"统计项": "❌ FAIL", "值": failed},
            {"统计项": "成功率", "值": success_rate},
            {"统计项": "错误次数", "值": len(self.errors)},
            {"统计项": "最后更新时间", "值": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
        ]

        # 按轮次汇总
        rounds = {}
        for r in self.records:
            rnd = r.get("测试轮次", "未知")
            if rnd not in rounds:
                rounds[rnd] = {"total": 0, "pass": 0}
            rounds[rnd]["total"] += 1
            if r.get("测试结果") == "PASS":
                rounds[rnd]["pass"] += 1

        for rnd, stats in sorted(rounds.items(), key=lambda x: x[0]):
            rate = f"{(stats['pass'] / stats['total'] * 100):.1f}%" if stats['total'] > 0 else "N/A"
            summary.append(
                {"统计项": f"  └ {rnd}", "值": f"✅ {stats['pass']} / ❌ {stats['total'] - stats['pass']} ({rate})"})

        # 按测试类型汇总
        types = {}
        for r in self.records:
            t = r.get("测试类型", "未知")
            if t not in types:
                types[t] = {"total": 0, "pass": 0}
            types[t]["total"] += 1
            if r.get("测试结果") == "PASS":
                types[t]["pass"] += 1

        for t, stats in sorted(types.items()):
            rate = f"{(stats['pass'] / stats['total'] * 100):.1f}%" if stats['total'] > 0 else "N/A"
            summary.append(
                {"统计项": f"  └ {t}", "值": f"✅ {stats['pass']} / ❌ {stats['total'] - stats['pass']} ({rate})"})

        return summary