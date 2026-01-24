"""
加班报销自动化 Agent 配置文件
"""

# 打卡记录表列索引（基于企业微信导出格式）
ATTENDANCE_COLUMNS = {
    "日期": 0,           # 第一列：日期
    "姓名": 1,           # 第二列：姓名
    "最早打卡": 7,       # 最早打卡时间
    "最晚打卡": 8,       # 最晚打卡时间
    "标准工时": 10,      # 标准工作时长(小时)
    "实际工时": 11,      # 实际工作时长(小时)
    "考勤结果": 13,      # 考勤结果
    "上班打卡时间": 53,  # 上班1 打卡时间
    "下班打卡时间": 55,  # 下班1 打卡时间
}

# 数据起始行（跳过表头）
DATA_START_ROW = 4

# 标准工作时长（小时）
STANDARD_WORK_HOURS = 8

# 加班最低时长阈值（小时），低于此时长不计入加班
MIN_OVERTIME_HOURS = 1

# 输出文件名
OUTPUT_FILES = {
    "excel_report": "报销单.xlsx",
    "word_summary": "报销材料汇总.docx",
}

# OCR 配置
OCR_CONFIG = {
    "language": "chi_sim+eng",  # 简体中文 + 英文
    "dpi": 300,
}
