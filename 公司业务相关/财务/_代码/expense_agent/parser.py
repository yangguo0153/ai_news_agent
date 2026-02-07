"""
打卡记录表解析器

解析企业微信导出的打卡记录表，提取加班信息。
"""

import pandas as pd
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from .config import ATTENDANCE_COLUMNS, DATA_START_ROW, STANDARD_WORK_HOURS, MIN_OVERTIME_HOURS


@dataclass
class AttendanceRecord:
    """打卡记录"""
    date: str              # 日期，如 "2026/01/20"
    weekday: str           # 星期，如 "星期二"
    name: str              # 姓名
    clock_in: str          # 上班打卡时间
    clock_out: str         # 下班打卡时间
    standard_hours: float  # 标准工时
    actual_hours: float    # 实际工时
    overtime_hours: float  # 加班时长
    status: str            # 考勤状态
    
    @property
    def date_str(self) -> str:
        """获取格式化的日期字符串 YYYY-MM-DD"""
        try:
            # 处理 "2026/01/20 星期二" 格式
            date_part = self.date.split()[0] if " " in self.date else self.date
            dt = datetime.strptime(date_part, "%Y/%m/%d")
            return dt.strftime("%Y-%m-%d")
        except:
            return self.date
    
    @property
    def is_overtime(self) -> bool:
        """是否有加班"""
        return self.overtime_hours >= MIN_OVERTIME_HOURS


class AttendanceParser:
    """打卡记录表解析器"""
    
    def __init__(self, excel_path: str):
        self.excel_path = Path(excel_path)
        self.records: List[AttendanceRecord] = []
    
    def parse(self) -> List[AttendanceRecord]:
        """解析 Excel 文件，返回加班记录列表"""
        if not self.excel_path.exists():
            raise FileNotFoundError(f"打卡记录表不存在: {self.excel_path}")
        
        # 读取 Excel，不使用表头
        df = pd.read_excel(self.excel_path, header=None)
        
        # 从数据起始行开始遍历
        for idx in range(DATA_START_ROW, len(df)):
            row = df.iloc[idx]
            
            # 跳过空行
            if pd.isna(row[0]):
                continue
            
            # 提取日期和星期
            date_cell = str(row[ATTENDANCE_COLUMNS["日期"]])
            if " " in date_cell:
                date_part, weekday = date_cell.rsplit(" ", 1)
            else:
                date_part, weekday = date_cell, ""
            
            # 提取工时
            try:
                standard_hours = float(row[ATTENDANCE_COLUMNS["标准工时"]]) if pd.notna(row[ATTENDANCE_COLUMNS["标准工时"]]) else STANDARD_WORK_HOURS
            except:
                standard_hours = STANDARD_WORK_HOURS
            
            try:
                actual_hours = float(row[ATTENDANCE_COLUMNS["实际工时"]]) if pd.notna(row[ATTENDANCE_COLUMNS["实际工时"]]) else 0
            except:
                actual_hours = 0
            
            # 计算加班时长
            overtime_hours = max(0, actual_hours - standard_hours)
            
            # 提取打卡时间
            clock_in = str(row[ATTENDANCE_COLUMNS["上班打卡时间"]]) if pd.notna(row[ATTENDANCE_COLUMNS["上班打卡时间"]]) else "--"
            clock_out = str(row[ATTENDANCE_COLUMNS["下班打卡时间"]]) if pd.notna(row[ATTENDANCE_COLUMNS["下班打卡时间"]]) else "--"
            
            # 提取考勤状态
            status = str(row[ATTENDANCE_COLUMNS["考勤结果"]]) if pd.notna(row[ATTENDANCE_COLUMNS["考勤结果"]]) else ""
            
            record = AttendanceRecord(
                date=date_cell,
                weekday=weekday,
                name=str(row[ATTENDANCE_COLUMNS["姓名"]]) if pd.notna(row[ATTENDANCE_COLUMNS["姓名"]]) else "",
                clock_in=clock_in,
                clock_out=clock_out,
                standard_hours=standard_hours,
                actual_hours=actual_hours,
                overtime_hours=overtime_hours,
                status=status,
            )
            
            self.records.append(record)
        
        return self.records
    
    def get_overtime_records(self) -> List[AttendanceRecord]:
        """获取有加班的记录"""
        if not self.records:
            self.parse()
        return [r for r in self.records if r.is_overtime]


if __name__ == "__main__":
    # 测试
    import sys
    if len(sys.argv) > 1:
        parser = AttendanceParser(sys.argv[1])
        records = parser.parse()
        print(f"共解析 {len(records)} 条记录")
        for r in parser.get_overtime_records():
            print(f"  {r.date_str}: 加班 {r.overtime_hours} 小时")
