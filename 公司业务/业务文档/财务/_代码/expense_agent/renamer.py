"""
文件重命名模块

利用 OCR 识别结果，结合打卡记录，对文件进行重命名。
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from .parser import AttendanceRecord
from .ocr_engine import OCREngine


class FileRenamer:
    """文件重命名器"""
    
    def __init__(self, records: List[AttendanceRecord]):
        self.records = records
        self.record_map = {r.date_str: r for r in records}
        self.ocr = OCREngine()
        
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """
        将各种日期格式标准化为 YYYY-MM-DD

        支持的格式:
        - 2026/1/20, 2026/01/20 (斜杠分隔)
        - 2026-1-20, 2026-01-20 (连字符分隔)
        - 2026年1月20日, 2026年01月20日 (中文格式)
        """
        if not date_str:
            return None

        date_str = date_str.strip()

        # 格式1: 2026年01月20日 或 2026年1月20日
        try:
            # 先尝试带补零的格式
            dt = datetime.strptime(date_str, "%Y年%m月%d日")
            return dt.strftime("%Y-%m-%d")
        except:
            pass

        # 格式2: 2026/1/20 或 2026/01/20 (斜杠分隔)
        if "/" in date_str:
            parts = date_str.split("/")
            if len(parts) == 3:
                try:
                    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                    return f"{year:04d}-{month:02d}-{day:02d}"
                except:
                    pass

        # 格式3: 2026-1-20 或 2026-01-20 (连字符分隔，可能没补零)
        if "-" in date_str:
            parts = date_str.split("-")
            if len(parts) == 3:
                try:
                    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                    return f"{year:04d}-{month:02d}-{day:02d}"
                except:
                    pass

        # 已经是标准格式
        if len(date_str) == 10 and date_str[4] == "-" and date_str[7] == "-":
            return date_str

        return None

    def _find_record_by_date(self, date_str: str) -> Optional[AttendanceRecord]:
        """根据日期查找打卡记录"""
        # 标准化日期格式
        normalized = self._normalize_date(date_str)

        if normalized and normalized in self.record_map:
            return self.record_map[normalized]

        # 原始字符串也尝试匹配
        if date_str in self.record_map:
            return self.record_map[date_str]

        return None

    def rename_screenshots(self, input_dir: str, output_dir: str, type_prefix: str = "") -> List[str]:
        """重命名截图文件"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        renamed_files = []

        if not input_path.exists():
            print(f"⚠️  目录不存在: {input_dir}")
            return []

        print(f"📂 正在处理截图目录: {input_dir}")

        # 第一遍：处理所有文件，收集已识别日期的加班申请截图
        all_files = list(input_path.glob("*.[pP][nN][gG]"))
        identified_overtime_apps = {}  # {文件修改时间: (日期, 记录)}
        unidentified_files = []  # 未识别日期的文件

        for file_path in all_files:
            text = self.ocr.extract_text_from_image(str(file_path))
            info = self.ocr.extract_overtime_reason(str(file_path))

            target_record = None
            if info.date:
                target_record = self._find_record_by_date(info.date)

            # 判断图片类型
            clock_in_keywords = ["导出报表", "9:00", "18:00", "打卡", "考勤", "上下班"]
            overtime_keywords = ["加班", "开始时间", "结束时间", "工作内容", "加班地点"]
            is_overtime = any(k in text for k in overtime_keywords)

            if target_record:
                mtime = file_path.stat().st_mtime
                if is_overtime:
                    identified_overtime_apps[mtime] = (target_record.date_str, target_record, file_path)
            else:
                unidentified_files.append((file_path, text))

        # 第二遍：为未识别的打卡截图匹配最近的加班申请截图
        # 构建加班申请截图的文件序号映射
        import re as regex
        overtime_by_seq = {}  # {序号: (日期, 记录)}
        for mtime, (date_str, record, ot_file) in identified_overtime_apps.items():
            seq_match = regex.search(r'(\d+)', ot_file.name)
            if seq_match:
                overtime_by_seq[int(seq_match.group(1))] = (date_str, record)

        for file_path, text in unidentified_files:
            is_clock_in = any(k in text for k in clock_in_keywords)
            # 加班申请的特有关键词（不会出现在打卡截图中）
            # 注意："审批"可能出现在打卡截图的"审批中"状态中，所以不使用
            overtime_specific_keywords = ["开始时间", "结束时间", "加班地点", "加班事由", "加班打卡截图"]
            is_overtime_specific = any(k in text for k in overtime_specific_keywords)

            # 如果是打卡截图且未识别日期，尝试基于文件名序号配对
            # 打卡截图特征：包含打卡关键词，且不包含加班申请特有关键词
            if is_clock_in and not is_overtime_specific and overtime_by_seq:
                seq_match = regex.search(r'(\d+)', file_path.name)
                if seq_match:
                    seq = int(seq_match.group(1))
                    # 尝试匹配相邻的加班申请截图（序号+1或+2）
                    best_match = None
                    for delta in [1, 2, 3]:
                        if seq + delta in overtime_by_seq:
                            best_match = overtime_by_seq[seq + delta]
                            break

                    if best_match:
                        date_str, target_record = best_match
                        hours = int(target_record.overtime_hours) if target_record.overtime_hours % 1 == 0 else target_record.overtime_hours
                        new_name = f"{date_str}_加班{hours}小时_打卡.png"
                        target_path = output_path / new_name
                        shutil.copy2(file_path, target_path)
                        renamed_files.append(str(target_path))
                        print(f"  🔍 分析文件: {file_path.name}")
                        print(f"    ✅ 基于序号配对重命名为: {new_name}")
                        continue

            # 未能配对的文件，保留原名
            shutil.copy2(file_path, output_path / file_path.name)
            renamed_files.append(str(output_path / file_path.name))
            print(f"  🔍 分析文件: {file_path.name}")
            print(f"    ⚠️  未找到匹配的日期记录，跳过rename，直接复制")

        # 第三遍：处理已识别的加班申请截图
        for mtime, (date_str, target_record, file_path) in identified_overtime_apps.items():
            hours = int(target_record.overtime_hours) if target_record.overtime_hours % 1 == 0 else target_record.overtime_hours
            new_name = f"{date_str}_加班{hours}小时_加班申请.png"
            target_path = output_path / new_name
            shutil.copy2(file_path, target_path)
            renamed_files.append(str(target_path))
            print(f"  🔍 分析文件: {file_path.name}")
            print(f"    ✅ 重命名为: {new_name}")

        return renamed_files

    def rename_invoices(self, input_dir: str, output_dir: str, unmatched_dir: str = None) -> Dict[str, List[Dict]]:
        """
        重命名发票和行程单

        返回:
            {
                "matched": [...],    # 匹配成功（有加班记录）的发票
                "unmatched": [...]   # 无法匹配（无加班记录）的发票
            }
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 无法匹配的文件输出目录
        if unmatched_dir:
            unmatched_path = Path(unmatched_dir)
            unmatched_path.mkdir(parents=True, exist_ok=True)
        else:
            unmatched_path = output_path.parent / "无法匹配"
            unmatched_path.mkdir(parents=True, exist_ok=True)

        matched_items = []
        unmatched_items = []

        if not input_path.exists():
            print(f"⚠️  目录不存在: {input_dir}")
            return {"matched": [], "unmatched": []}

        print(f"📂 正在处理发票目录: {input_dir}")
        for file_path in input_path.glob("*.[pP][dD][fF]"):
            print(f"  🔍 分析文件: {file_path.name}")

            # OCR 识别发票信息
            info = self.ocr.extract_taxi_invoice_info(str(file_path))

            if info.date:
                # 使用统一的日期标准化方法
                normalized_date = self._normalize_date(info.date) or info.date
                target_record = self._find_record_by_date(info.date)

                # 构造文件名: 2026-01-20_发票_35元.pdf
                amount_str = f"{int(info.amount)}" if info.amount % 1 == 0 else f"{info.amount}"
                new_name = f"{normalized_date}_发票_{amount_str}元.pdf"

                # 检查是否有加班记录（加班时长 > 0）
                has_overtime = target_record and target_record.overtime_hours > 0

                if has_overtime:
                    # 匹配成功：有加班记录
                    target_path = output_path / new_name
                    shutil.copy2(file_path, target_path)
                    matched_items.append({
                        "path": str(target_path),
                        "info": info,
                        "record": target_record
                    })
                    print(f"    ✅ 匹配成功: {new_name} (加班 {target_record.overtime_hours}h)")
                else:
                    # 无法匹配：无加班记录或加班时长为0
                    target_path = unmatched_path / new_name
                    shutil.copy2(file_path, target_path)
                    unmatched_items.append({
                        "path": str(target_path),
                        "info": info,
                        "record": target_record,
                        "reason": "无加班记录" if not target_record else "当日无加班"
                    })
                    reason = "无加班记录" if not target_record else "当日无加班"
                    print(f"    ⚠️  无法匹配: {new_name} ({reason})")
            else:
                # 无法提取日期，归入无法匹配
                target_path = unmatched_path / file_path.name
                shutil.copy2(file_path, target_path)
                unmatched_items.append({
                    "path": str(target_path),
                    "info": info,
                    "record": None,
                    "reason": "无法识别日期"
                })
                print(f"    ⚠️  无法匹配: {file_path.name} (无法识别日期)")

        return {"matched": matched_items, "unmatched": unmatched_items}

    def _get_overtime_map(self) -> Dict[str, float]:
        """获取加班记录映射 {日期: 加班时长}"""
        return {r.date_str: r.overtime_hours for r in self.records if r.overtime_hours > 0}

    def _match_trip_date(self, trip_date: str, trip_time: str) -> tuple:
        """
        智能匹配行程日期到加班记录

        凌晨0-6点的行程:
        - 优先匹配前一天（前一天加班后回家）
        - 如果前一天没有加班，尝试匹配当天（当天加班到凌晨）

        返回: (matched_date, overtime_hours, note)
        """
        overtime_map = self._get_overtime_map()
        hour = int(trip_time.split(':')[0])

        if hour < 6:  # 凌晨0-6点
            dt = datetime.strptime(trip_date, "%Y-%m-%d")
            prev_day = (dt - timedelta(days=1)).strftime("%Y-%m-%d")

            # 优先匹配前一天
            if prev_day in overtime_map:
                return prev_day, overtime_map[prev_day], f"匹配前一天{prev_day}"
            # 前一天无加班，尝试当天
            elif trip_date in overtime_map:
                return trip_date, overtime_map[trip_date], "当天加班到凌晨"
            else:
                return prev_day, 0, f"匹配前一天{prev_day}"
        else:
            # 非凌晨，直接匹配当天
            overtime = overtime_map.get(trip_date, 0)
            return trip_date, overtime, ""

    def process_trip_sheets(self, input_dir: str, output_dir: str, unmatched_dir: str = None) -> Dict:
        """
        处理行程单，核对每条行程与加班记录

        返回:
            {
                "matched_trips": [...],    # 可报销的行程
                "unmatched_trips": [...],  # 无法报销的行程
                "matched_amount": float,   # 可报销金额
                "unmatched_amount": float, # 无法报销金额
                "files": {...}             # 文件处理结果
            }
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        if unmatched_dir:
            unmatched_path = Path(unmatched_dir)
        else:
            unmatched_path = output_path.parent / "无法匹配"
        unmatched_path.mkdir(parents=True, exist_ok=True)

        result = {
            "matched_trips": [],
            "unmatched_trips": [],
            "matched_amount": 0.0,
            "unmatched_amount": 0.0,
            "files": {"matched": [], "unmatched": []}
        }

        if not input_path.exists():
            print(f"⚠️  目录不存在: {input_dir}")
            return result

        print(f"📂 正在处理行程单目录: {input_dir}")

        # 查找行程单文件（包含"行程"关键字的PDF）
        for file_path in input_path.glob("*.[pP][dD][fF]"):
            filename = file_path.name
            is_trip_sheet = "行程" in filename

            if is_trip_sheet:
                print(f"  📋 解析行程单: {filename}")
                trip_info = self.ocr.extract_trip_sheet_info(str(file_path))

                file_matched_trips = []
                file_unmatched_trips = []

                for trip in trip_info.trips:
                    matched_date, overtime, note = self._match_trip_date(trip.date, trip.time)

                    if overtime > 0:
                        print(f"    ✅ {trip.date} {trip.time} {note} -> 加班{overtime}h")
                        file_matched_trips.append({
                            "date": trip.date,
                            "time": trip.time,
                            "matched_date": matched_date,
                            "overtime": overtime,
                            "amount": trip.amount,
                            "origin": trip.origin,
                            "destination": trip.destination
                        })
                        result["matched_trips"].append({
                            "date": trip.date,
                            "time": trip.time,
                            "matched_date": matched_date,
                            "overtime": overtime,
                            "amount": trip.amount,
                            "origin": trip.origin,
                            "destination": trip.destination
                        })
                    else:
                        print(f"    ❌ {trip.date} {trip.time} {note} -> 无加班记录")
                        file_unmatched_trips.append({
                            "date": trip.date,
                            "time": trip.time,
                            "reason": "无加班记录"
                        })
                        result["unmatched_trips"].append({
                            "date": trip.date,
                            "time": trip.time,
                            "reason": "无加班记录"
                        })

                # 复制行程单到对应目录（如果有匹配的行程就放matched，否则放unmatched）
                if file_matched_trips:
                    target = output_path / filename
                    shutil.copy2(file_path, target)
                    result["files"]["matched"].append(str(target))
                else:
                    target = unmatched_path / filename
                    shutil.copy2(file_path, target)
                    result["files"]["unmatched"].append(str(target))

        return result
