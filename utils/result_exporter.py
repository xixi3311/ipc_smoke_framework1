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
                df = pd.read_excel(self.excel_path, sheet_name="测试明细")
                self.records = df.to_dict("records")

                # 把 Excel 图标还原成内部状态文本，避免重复映射
                for record in self.records:
                    value = record.get("测试结果", "")
                    if value == "✅":
                        record["测试结果"] = "PASS"
                    elif value == "❌":
                        record["测试结果"] = "FAIL"
                    elif value in ("⏭️", "⚠️"):
                        record["测试结果"] = "SKIP"

                # 读取历史错误详情，避免下一次保存时丢失错误记录
                try:
                    error_df = pd.read_excel(self.excel_path, sheet_name="错误详情")
                    self.errors = error_df.to_dict("records")
                except Exception:
                    self.errors = []

            except Exception as e:
                print(f"[Exporter] 读取已有数据失败: {e}")

    def record_result(self, round_num: int, test_type: str, mode: str,
                      biz_type: str, duration: float, success: bool = None,
                      remark: str = "", status: str = None):
        """
        记录测试结果。

        status 用于明确记录 PASS、FAIL、SKIP。
        success 参数保留，兼容项目中原有的调用方式。
        """

        # 新调用传入 status；旧调用仍可传 success
        if status is None:
            status = "PASS" if success else "FAIL"

        status = str(status).upper()
        if status not in ("PASS", "FAIL", "SKIP"):
            raise ValueError(f"不支持的测试结果状态: {status}")

        # 截断备注，避免 Excel 单元格内容过长
        remark = str(remark)[:500] if remark else ""

        data = {
            "设备名称": config.DEVICE_NAME,
            "设备 SN": str(config.DEVICE_SN),
            "测试轮次": f"第 {round_num} 轮",
            "测试类型": test_type,
            "工作模式": mode if mode else "-",
            "业务类型": biz_type,
            "耗时(秒)": round(duration, 2) if duration else "N/A",
            "测试结果": status,
            "记录时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "备注": remark
        }

        self.records.append(data)
        self.save_to_excel()

    def record_error(self, round_num: int, test_type: str, test_case: str, error_msg: str):
        """记录失败用例的错误详情；SKIP 不应调用此方法"""

        error_msg = str(error_msg)[:500]
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
            with pd.ExcelWriter(self.excel_path, engine="openpyxl") as writer:
                # Sheet1：测试明细
                if self.records:
                    df = pd.DataFrame(self.records)

                    # 避免 SN 被 Excel 转成科学计数法
                    df["设备 SN"] = df["设备 SN"].astype(str)

                    # PASS / FAIL / SKIP 映射为 Excel 图标
                    df["测试结果"] = df["测试结果"].map({
                        "PASS": "✅",
                        "FAIL": "❌",
                        "SKIP": "⏭️"
                    })

                    df.to_excel(writer, sheet_name="测试明细", index=False)
                    self._adjust_column_width(writer.sheets["测试明细"])

                # Sheet2：汇总统计
                summary = self._build_summary()
                df_summary = pd.DataFrame(summary)
                df_summary.to_excel(writer, sheet_name="汇总统计", index=False)
                self._adjust_column_width(writer.sheets["汇总统计"])

                # Sheet3：错误详情
                if self.errors:
                    df_errors = pd.DataFrame(self.errors)
                    df_errors.to_excel(writer, sheet_name="错误详情", index=False)
                    self._adjust_column_width(writer.sheets["错误详情"])

            print(f"[Exporter] 数据已同步至: {self.excel_path}")
        except Exception as e:
            print(f"[Exporter Err] 保存 Excel 失败: {e}")

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
                except Exception:
                    pass

            # 最大列宽限制为 50，避免列过宽
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

    def _build_summary(self):
        """生成总计、轮次和测试类型统计"""

        # PASS、FAIL、SKIP 分开统计，SKIP 不计入失败数
        passed = sum(1 for record in self.records if record.get("测试结果") == "PASS")
        failed = sum(1 for record in self.records if record.get("测试结果") == "FAIL")
        skipped = sum(1 for record in self.records if record.get("测试结果") == "SKIP")
        total = len(self.records)

        # 成功率只按实际执行的 PASS + FAIL 计算
        executed = passed + failed
        success_rate = f"{passed / executed * 100:.1f}%" if executed else "N/A"

        summary = [
            {"统计项": "设备名称", "值": config.DEVICE_NAME},
            {"统计项": "设备 SN", "值": str(config.DEVICE_SN)},
            {"统计项": "总记录数", "值": total},
            {"统计项": "✅ PASS", "值": passed},
            {"统计项": "❌ FAIL", "值": failed},
            {"统计项": "⏭️ SKIP", "值": skipped},
            {"统计项": "成功率", "值": success_rate},
            {"统计项": "错误次数", "值": len(self.errors)},
            {"统计项": "最后更新时间", "值": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        ]

        # 按轮次汇总
        rounds = {}
        for record in self.records:
            round_name = record.get("测试轮次", "未知")
            if round_name not in rounds:
                rounds[round_name] = {"pass": 0, "fail": 0, "skip": 0}

            result = record.get("测试结果")
            if result == "PASS":
                rounds[round_name]["pass"] += 1
            elif result == "FAIL":
                rounds[round_name]["fail"] += 1
            elif result == "SKIP":
                rounds[round_name]["skip"] += 1

        for round_name, stats in sorted(rounds.items(), key=lambda item: item[0]):
            executed = stats["pass"] + stats["fail"]
            rate = f"{stats['pass'] / executed * 100:.1f}%" if executed else "N/A"
            summary.append({
                "统计项": f"  {round_name}",
                "值": (
                    f"✅ {stats['pass']} / ❌ {stats['fail']} / "
                    f"⏭️ {stats['skip']} ({rate})"
                )
            })

        # 按测试类型汇总
        types = {}
        for record in self.records:
            test_type = record.get("测试类型", "未知")
            if test_type not in types:
                types[test_type] = {"pass": 0, "fail": 0, "skip": 0}

            result = record.get("测试结果")
            if result == "PASS":
                types[test_type]["pass"] += 1
            elif result == "FAIL":
                types[test_type]["fail"] += 1
            elif result == "SKIP":
                types[test_type]["skip"] += 1

        for test_type, stats in sorted(types.items()):
            executed = stats["pass"] + stats["fail"]
            rate = f"{stats['pass'] / executed * 100:.1f}%" if executed else "N/A"
            summary.append({
                "统计项": f"  {test_type}",
                "值": (
                    f"✅ {stats['pass']} / ❌ {stats['fail']} / "
                    f"⏭️ {stats['skip']} ({rate})"
                )
            })

        return summary