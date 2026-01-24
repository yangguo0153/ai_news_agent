"""
加班报销自动化 Agent 主程序
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径，以便导入 expense_agent 模块
sys.path.append(str(Path(__file__).parent.parent))

from expense_agent.config import OUTPUT_FILES
from expense_agent.parser import AttendanceParser
from expense_agent.renamer import FileRenamer
from expense_agent.excel_generator import ExcelGenerator, ExpenseItem
from expense_agent.word_generator import WordGenerator


def extract_date_range(filename: str) -> str:
    """从文件名中提取日期范围，如 '20260118-20260120'"""
    # 匹配 YYYYMMDD-YYYYMMDD 格式
    match = re.search(r'(\d{8}-\d{8})', filename)
    if match:
        return match.group(1)

    # 匹配 YYYY-MM-DD_YYYY-MM-DD 格式
    match = re.search(r'(\d{4}-\d{2}-\d{2}_\d{4}-\d{2}-\d{2})', filename)
    if match:
        return match.group(1).replace("-", "").replace("_", "-")

    return None


import shutil

def process_reimbursement(input_dir: Path, output_dir: Path, config: dict = None):
    """
    处理报销流程核心逻辑
    :param input_dir: 输入文件夹路径
    :param output_dir: 输出文件夹路径
    :param config: 配置字典 (e.g. {"overtime_start": "19:00", "taxi_limit": 200})
    """
    if config is None:
        config = {}
        
    print(f"🔧 使用配置: {config}")
    
    renamed_dir = output_dir / "已命名"
    print_dir = output_dir / "打印"
    
    # 确保基础输出目录存在
    renamed_dir.mkdir(parents=True, exist_ok=True)
    print_dir.mkdir(parents=True, exist_ok=True)

    # 检查输入文件 - 查找 Excel 文件
    excel_files = list(input_dir.glob("*.xlsx"))
    if not excel_files:
        print("❌ 未找到打卡记录表 (.xlsx)，请检查 '输入' 文件夹")
        return {"status": "error", "message": "未找到打卡记录表 (.xlsx)"}
    attendance_file = excel_files[0]
    print(f"📖 读取打卡记录表: {attendance_file.name}")

    # 从文件名提取日期范围作为阶段标识
    date_range = extract_date_range(attendance_file.name)
    if not date_range:
        print("⚠️  无法从文件名提取日期范围，使用默认文件夹结构")
        date_range = datetime.now().strftime("%Y%m%d")

    print(f"📆 报销阶段: {date_range}")

    # 阶段性文件夹结构
    
    input_screenshots_dir = input_dir / "打卡和加班截图" / date_range
    input_invoices_dir = input_dir / "打车发票和行程单" / date_range
    
    # 如果标准目录不存在，尝试直接在 input_dir 下查找（适配 Web 上传解压后的简化结构）
    if not input_screenshots_dir.exists():
         input_screenshots_dir = input_dir / "打卡和加班截图"
    if not input_invoices_dir.exists():
         input_invoices_dir = input_dir / "打车发票和行程单"

    output_screenshots_dir = renamed_dir / "打卡和加班截图" / date_range
    output_invoices_dir = renamed_dir / "打车发票和行程单" / date_range
    unmatched_invoices_dir = renamed_dir / "无法匹配" / date_range
    stage_print_dir = print_dir / date_range

    # 确保输出目录存在
    output_screenshots_dir.mkdir(parents=True, exist_ok=True)
    output_invoices_dir.mkdir(parents=True, exist_ok=True)
    unmatched_invoices_dir.mkdir(parents=True, exist_ok=True)
    stage_print_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. 解析打卡记录
    try:
        # TODO: 传递配置给 Parser (如标准工时等，如果有需要)
        parser = AttendanceParser(str(attendance_file))
        records = parser.parse()
        overtime_records = parser.get_overtime_records()
        print(f"📊 解析完成: 共 {len(records)} 条记录，其中 {len(overtime_records)} 条有加班")
    except Exception as e:
        print(f"❌ 解析 Excel 失败: {e}")
        return {"status": "error", "message": f"解析 Excel 失败: {e}"}

    # 3. 文件重命名
    print("\n🔄 开始整理并重命名文件...")
    renamer = FileRenamer(records)

    # A. 处理打卡和加班截图
    print("--- 处理打卡和加班截图 ---")
    if input_screenshots_dir.exists():
        all_screenshots = renamer.rename_screenshots(
            str(input_screenshots_dir),
            str(output_screenshots_dir),
            type_prefix=""
        )
    else:
        print(f"⚠️  未找到截图目录: {input_screenshots_dir}")
        all_screenshots = []

    # B. 处理行程单
    print("--- 处理行程单 ---")
    if input_invoices_dir.exists():
        # 传递 taxi_limit 配置给处理逻辑
        taxi_limit = config.get("taxi_limit", 200)
        # 目前 FileRenamer.process_trip_sheets 还没有用 limit，暂时只是打印
        print(f"   ℹ️  每日打车限额: {taxi_limit}元 (逻辑待集成)")
        
        trip_results = renamer.process_trip_sheets(
            str(input_invoices_dir),
            str(output_invoices_dir),
            str(unmatched_invoices_dir)
        )
        matched_trips = trip_results["matched_trips"]
        unmatched_trips = trip_results["unmatched_trips"]
        trip_sheet_files = trip_results["files"]["matched"]
    else:
        print(f"⚠️  未找到行程单目录: {input_invoices_dir}")
        matched_trips = []
        unmatched_trips = []
        trip_sheet_files = []

    # C. 处理发票
    print("--- 处理发票文件 ---")
    if input_invoices_dir.exists():
        for file_path in input_invoices_dir.glob("*.[pP][dD][fF]"):
            if "行程" not in file_path.name:  # 发票文件
                target = output_invoices_dir / file_path.name
                shutil.copy2(file_path, target)
                print(f"  📄 复制发票: {file_path.name}")

    # 4. 生成 Excel 报销单
    print("\n📝 生成 Excel 报销单...")
    excel_gen = ExcelGenerator()
    sorted_trips = sorted(matched_trips, key=lambda x: (x.get("matched_date", ""), x.get("time", "")))

    for idx, trip in enumerate(sorted_trips, 1):
        matched_date = trip.get("matched_date", trip["date"])
        overtime = trip.get("overtime", 0)
        origin = trip.get("origin", "") or "公司"
        destination = trip.get("destination", "") or "家"
        
        # 检查是否超过限额 (虽然这里只是生成，但可以标记)
        amount = trip.get("amount", 0)
        # notes = " (超额)" if amount > taxi_limit else ""
        
        expense = ExpenseItem(
            序号=idx,
            日期=matched_date,
            加班时间=f"加班{overtime}h",
            出发地=origin,
            到达地=destination,
            金额=amount,
        )
        excel_gen.add_item(expense)

    if sorted_trips:
        report_path = excel_gen.generate(str(stage_print_dir / OUTPUT_FILES["excel_report"]))
        print(f"✅ 报销单已生成: {report_path}")
    
    # 5. 生成 Word 汇总材料
    print("\n📚 生成 Word 汇总材料...")
    word_gen = WordGenerator()

    # 5.1 打卡和加班截图
    from collections import defaultdict
    date_groups = defaultdict(list)
    for screenshot in all_screenshots:
        filename = Path(screenshot).name
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
        date_str = date_match.group(1) if date_match else "0000-00-00"
        date_groups[date_str].append(screenshot)

    def type_priority(fname):
        filename = Path(fname).name
        if "打卡" in filename: return 1
        return 2 if "加班申请" in filename else 3

    for date_str in sorted(date_groups.keys()):
        group = sorted(date_groups[date_str], key=type_priority)
        word_gen.add_images_to_page(group, max_per_row=2)
    
    if all_screenshots:
        word_gen.add_page_break()

    # 5.2 打车发票
    invoice_files = list(output_invoices_dir.glob("*发票*.pdf")) + list(output_invoices_dir.glob("*发票*.PDF"))
    if invoice_files:
        word_gen.add_pdf_screenshots_compact([str(f) for f in invoice_files], per_page=2)

    # 5.3 行程单
    if trip_sheet_files:
        if invoice_files: word_gen.add_page_break()
        word_gen.add_pdf_screenshots(trip_sheet_files, max_per_row=1)

    summary_path = word_gen.save(str(stage_print_dir / OUTPUT_FILES["word_summary"]))
    print(f"✅ 汇总材料已生成: {summary_path}")

    return {
        "status": "success",
        "generated_files": [str(stage_print_dir / OUTPUT_FILES["excel_report"]), str(summary_path)],
        "stats": {
            "matched": len(matched_trips),
            "unmatched": len(unmatched_trips),
            "total_amount": excel_gen.total_amount
        }
    }

def main():
    print("=" * 60)
    print("🚀 加班报销自动化 Agent 启动")
    print(f"📅 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    base_dir = Path("/Users/will/Desktop/通往AGI之路/公司业务相关/财务")
    input_dir = base_dir / "输入"
    output_dir = base_dir / "输出"
    
    process_reimbursement(input_dir, output_dir)

if __name__ == "__main__":
    main()
