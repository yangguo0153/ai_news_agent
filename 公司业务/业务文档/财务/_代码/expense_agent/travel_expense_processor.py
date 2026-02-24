"""
出差报销主处理器

协调 OCR、Excel更新、Word生成等模块，完成出差报销自动化流程
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# 导入模块
import sys
sys.path.append(str(Path(__file__).parent.parent))

from expense_agent.ocr_engine import OCREngine, TaxiInvoiceInfo, TripSheetInfo
from expense_agent.invoice_matcher import InvoiceMatcher, parse_invoice_pdf, parse_trip_sheet_pdf
from expense_agent.travel_excel_updater import TravelExcelUpdater, TravelExpenseItem, parse_date_to_display
from expense_agent.word_generator import WordGenerator
from expense_agent.config import get_travel_config
import re


def _parse_folder_date_range(folder_name: str) -> Dict:
    """
    从文件夹名称中解析日期范围

    支持的格式:
    - "125-129上海出差" -> 1月25日 到 1月29日
    - "0125-0129上海出差" -> 1月25日 到 1月29日
    - "1月25日-1月29日上海出差"

    :param folder_name: 文件夹名称
    :return: {"departure_date": "2026-01-25", "return_date": "2026-01-29", "trip_days": 5}
    """
    result = {
        "departure_date": "",
        "return_date": "",
        "trip_days": 0
    }

    # 模式1: "125-129" 或 "0125-0129" (简短格式)
    match = re.search(r'(\d{1,2})(\d{2})-(\d{1,2})(\d{2})', folder_name)
    if match:
        start_month = int(match.group(1))
        start_day = int(match.group(2))
        end_month = int(match.group(3))
        end_day = int(match.group(4))

        # 推断年份
        start_year = 2025 if start_month >= 11 else 2026
        end_year = 2025 if end_month >= 11 else 2026

        result["departure_date"] = f"{start_year}-{start_month:02d}-{start_day:02d}"
        result["return_date"] = f"{end_year}-{end_month:02d}-{end_day:02d}"

        # 计算天数
        try:
            d1 = datetime.strptime(result["departure_date"], "%Y-%m-%d")
            d2 = datetime.strptime(result["return_date"], "%Y-%m-%d")
            result["trip_days"] = (d2 - d1).days + 1
        except Exception:
            pass

        return result

    # 模式2: "1月25日-1月29日" (完整中文格式)
    match = re.search(r'(\d{1,2})月(\d{1,2})日-(\d{1,2})月(\d{1,2})日', folder_name)
    if match:
        start_month = int(match.group(1))
        start_day = int(match.group(2))
        end_month = int(match.group(3))
        end_day = int(match.group(4))

        start_year = 2025 if start_month >= 11 else 2026
        end_year = 2025 if end_month >= 11 else 2026

        result["departure_date"] = f"{start_year}-{start_month:02d}-{start_day:02d}"
        result["return_date"] = f"{end_year}-{end_month:02d}-{end_day:02d}"

        try:
            d1 = datetime.strptime(result["departure_date"], "%Y-%m-%d")
            d2 = datetime.strptime(result["return_date"], "%Y-%m-%d")
            result["trip_days"] = (d2 - d1).days + 1
        except Exception:
            pass

        return result

    return result


def process_travel_expense(trip_folder: Path, output_dir: Path, config_path: str = None):
    """
    处理单次出差报销
    :param trip_folder: 出差材料目录 (如 "125-129上海出差")
    :param output_dir: 输出目录
    :param config_path: 配置文件路径（可选）
    :return: 校验报告字典
    """
    print(f"🚀 开始处理出差报销: {trip_folder.name}")

    # 加载配置
    config = get_travel_config(config_path)

    # 初始化组件
    ocr = OCREngine()
    matcher = InvoiceMatcher()

    # 校验报告数据收集
    verification_report = {
        "trip_name": trip_folder.name,
        "items": [],  # 所有费用项
        "warnings": [],  # 警告信息
        "summary": {}  # 汇总信息
    }
    
    # 准备目录
    dirs = {
        "intercity": trip_folder / "01-城际交通",
        "taxi": trip_folder / "02-打车",
        "hotel": trip_folder / "03-酒店住宿",
        "general": trip_folder / "04-招待客户类",
        "subsidy": trip_folder / "05-差旅补助替票",
    }
    
    # 准备输出目录
    trip_output_dir = output_dir / trip_folder.name
    print_dir = trip_output_dir / "打印"
    unmatched_dir = trip_output_dir / "未对应"
    
    print_dir.mkdir(parents=True, exist_ok=True)
    unmatched_dir.mkdir(parents=True, exist_ok=True)
    
    # 查找 Excel 模版
    template_files = list(trip_folder.glob("*模版*.xlsx"))
    if not template_files:
        print("❌ 未找到 Excel 模版文件")
        return
    template_file = template_files[0]
    print(f"📄 使用模版: {template_file.name}")
    
    updater = TravelExcelUpdater(str(template_file))
    word_gen = WordGenerator()
    
    word_gen.add_title(f"出差报销材料 - {trip_folder.name}")
    
    # ================= 1. 处理城际交通 (确定天数) =================
    print("\n--- 处理城际交通 ---")
    trip_days = 0
    intercity_images = []

    if dirs["intercity"].exists():
        # 获取所有图片
        for file in dirs["intercity"].glob("*"):
            if file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                intercity_images.append(str(file))

        # 识别日期 - 使用新的多图片方法
        if intercity_images:
            # 从所有截图中提取去程和返程日期
            dates_info = ocr.extract_intercity_dates_from_multiple(intercity_images)
            dep_date = dates_info.get("departure_date", "")
            ret_date = dates_info.get("return_date", "")
            trip_days = dates_info.get("trip_days", 0)

            print(f"📅 OCR 识别行程: {dep_date} 至 {ret_date}")

            # 如果 OCR 只识别到一个日期或没有日期，尝试从文件夹名推断
            # 文件夹名格式: "125-129上海出差" -> 1月25日 到 1月29日
            if trip_days <= 1:
                folder_dates = _parse_folder_date_range(trip_folder.name)
                if folder_dates:
                    dep_date = folder_dates["departure_date"]
                    ret_date = folder_dates["return_date"]
                    trip_days = folder_dates["trip_days"]
                    print(f"📅 从文件夹名推断: {dep_date} 至 {ret_date}")

            print(f"⏳ 计算天数: {trip_days} 天")

            if trip_days > 0:
                updater.set_trip_days(trip_days)

        # Word 排版
        if intercity_images:
            word_gen.add_section_title("城际交通订单")
            word_gen.add_images_to_page(intercity_images, max_per_row=2)
    else:
        print("ℹ️ 无城际交通目录")

    # ================= 2. 处理打车 (发票+行程单) =================
    print("\n--- 处理打车报销 ---")
    taxi_invoices = []
    trip_sheets = []
    other_taxi_files = [] # 截图等
    
    if dirs["taxi"].exists():
        files = list(dirs["taxi"].glob("*"))
        
        # 分类文件
        for f in files:
            if f.name.startswith("._"): continue # 跳过临时文件
            
            if f.suffix.lower() == '.pdf':
                if "行程" in f.name:
                    info = parse_trip_sheet_pdf(str(f))
                    if info.total_amount > 0:
                        trip_sheets.append(info)
                    else:
                        print(f"⚠️ 忽略无效行程单: {f.name}")
                elif "发票" in f.name:
                    info = parse_invoice_pdf(str(f))
                    taxi_invoices.append(info)
                else:
                    # 尝试猜测
                    print(f"❓ 未知PDF类型，尝试解析: {f.name}")
                    if "行程" in ocr.extract_text_from_pdf(str(f)):
                        trip_sheets.append(parse_trip_sheet_pdf(str(f)))
                    else:
                        taxi_invoices.append(parse_invoice_pdf(str(f)))
            
            elif f.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                other_taxi_files.append(str(f))
        
        print(f"🧾 发现 {len(taxi_invoices)} 张打车发票, {len(trip_sheets)} 张行程单")
        
        # 匹配
        matches, unmatched_inv, unmatched_trip = matcher.match_invoices_to_trips(taxi_invoices, trip_sheets)
        
        print(f"✅ 匹配成功: {len(matches)} 对")
        if unmatched_inv:
            print(f"⚠️ 未匹配发票: {len(unmatched_inv)}")
            for inv in unmatched_inv:
                print(f"   - {Path(inv.file_path).name} (¥{inv.total_amount})")
                # 移动到未对应文件夹
                shutil.copy2(inv.file_path, unmatched_dir / Path(inv.file_path).name)
        
        if unmatched_trip:
            print(f"⚠️ 未匹配行程单: {len(unmatched_trip)}")
            for ts in unmatched_trip:
                shutil.copy2(ts.file_path, unmatched_dir / Path(ts.file_path).name)

        # 添加到 Excel
        word_gen.add_section_title("市内交通报销")
        
        # 按日期排序
        sorted_matches = sorted(matches, key=lambda m: m.invoice.date)
        
        for idx, match in enumerate(sorted_matches, 1):
            inv = match.invoice
            ts = match.trip_sheet
            
            # 1. 发票横版全页 (改为全宽竖版)
            if inv.file_path.lower().endswith('.pdf'):
                # PDF 转图片后添加
                import fitz
                try:
                    doc = fitz.open(inv.file_path)
                    page = doc[0]
                    # 提高 DPI 以保证清晰度
                    pix = page.get_pixmap(dpi=300)
                    img_path = f"{inv.file_path}_temp.jpg"
                    pix.save(img_path)
                    word_gen.add_invoice_full_width(img_path)
                    if os.path.exists(img_path): os.remove(img_path)
                    doc.close()
                except Exception as e:
                    print(f"⚠️ PDF转图片失败: {e}")
            else:
                word_gen.add_invoice_full_width(inv.file_path)

            # 2. 行程单 (跟在发票后面)
            word_gen.add_pdf_screenshots_compact([ts.file_path], per_page=1)
            word_gen.add_page_break()

            # Excel: 使用行程单明细 (已在 invoice_matcher 中尝试提取起终点)
            print(f"   📝 写入行程单明细 ({len(match.trips)} 笔)...")
            for trip in match.trips:
                # 备注: 时间 起点→终点 (如果提取到了)
                notes_parts = [trip.time]
                if trip.origin: notes_parts.append(trip.origin)
                if trip.destination: notes_parts.append(f"{config.route_separator}{trip.destination}")
                note = " ".join(notes_parts)
                
                item = TravelExpenseItem(
                    日期=parse_date_to_display(trip.date),
                    费用名称="交通费(打车)",
                    单价=trip.amount,
                    数量=1,
                    费用金额=trip.amount,
                    备注=note
                )
                updater.add_item(item)

        # 处理截图类 (手动打车票据)
        if other_taxi_files:
            print(f"📸 处理 {len(other_taxi_files)} 张出租车票据截图")
            word_gen.add_subsection_title("其他打车票据(截图)")

            for img_path in other_taxi_files:
                # 解析文件名提取信息
                # 兼容 "_" 和 "-" 分隔
                filename = Path(img_path).stem
                filename_clean = filename.replace('-', '_')
                parts = filename_clean.split('_')

                amount = 0.0
                origin = ""
                dest = ""

                # 1. 尝试从文件名找金额
                import re
                try:
                    amount_match = re.search(r'(\d+\.?\d*)', parts[-1])
                    if amount_match:
                        amount = float(amount_match.group(1))
                except:
                    pass

                # 2. 如果文件名没金额，OCR 识别
                if amount == 0:
                    print(f"   🔍 文件名未含金额，尝试 OCR 识别: {filename}...")
                    ocr_text = ocr.extract_text_from_image(str(img_path))
                    # 找最大的金额 (通常是总价)
                    all_amounts = re.findall(r'(\d+\.\d{2})', ocr_text)
                    if all_amounts:
                        try:
                            float_amounts = [float(x) for x in all_amounts]
                            amount = max(float_amounts)
                            print(f"      ✅ OCR 识别金额: ¥{amount}")
                        except:
                            pass

                # 3. 提取起终点 (假设文件名结构: 起点-终点...)
                if len(parts) >= 2:
                    origin = parts[0]
                    dest = parts[1]

                if amount > 0:
                    print(f"   ➕ 添加截图费用: ¥{amount} ({origin}{config.route_separator}{dest})")
                    item = TravelExpenseItem(
                        日期="",
                        费用名称="交通费(打车)",
                        单价=amount,
                        数量=1,
                        费用金额=amount,
                        备注=f"{origin}{config.route_separator}{dest}" if origin and dest else f"截图报销: {filename}"
                    )
                    updater.add_item(item)
                else:
                    print(f"   ⚠️ 未能提取金额: {filename}")

                # Word: 紧凑排版 (截图不需要占据整页)
                word_gen.add_images_to_page([img_path], max_per_row=2, compact=True)

    # ================= 3. 处理酒店住宿 =================
    print("\n--- 处理酒店住宿 ---")
    if dirs["hotel"].exists():
        hotel_files = list(dirs["hotel"].glob("*.pdf"))
        word_gen.add_section_title("住宿费")
        
        for pdf in hotel_files:
            info = ocr.extract_hotel_invoice(str(pdf))
            print(f"🏨 酒店: {info.get('hotel_name')} - ¥{info.get('amount')}")
            
            item = TravelExpenseItem(
                日期=parse_date_to_display(info.get("date", "")),
                费用名称="酒店",
                单价=info.get("amount", 0),
                数量=1,
                费用金额=info.get("amount", 0),
                备注=info.get("hotel_name", "")
            )
            updater.add_item(item)
            
            # Word 排版
            word_gen.add_pdf_screenshots_compact([str(pdf)], per_page=1)

    # ================= 4. 处理招待客户类 =================
    print("\n--- 处理招待客户类 ---")
    if dirs["general"].exists():
        general_files = list(dirs["general"].glob("*"))
        if general_files:
            word_gen.add_section_title("客户招待费")
        
        valid_files = [f for f in general_files if f.name.startswith(".") is False]
        
        for f in valid_files:
            info = ocr.extract_general_invoice(str(f))
            print(f"☕️ 招待: {info.get('type')} - ¥{info.get('amount')}")
            
            item = TravelExpenseItem(
                日期=parse_date_to_display(info.get("date", "")),
                费用名称=f"客户{info.get('type', '其他')}",
                单价=info.get("amount", 0),
                数量=1,
                费用金额=info.get("amount", 0),
                备注="招待客户"
            )
            updater.add_item(item)
            
            # Word 排版
            if f.suffix.lower() == '.pdf':
                word_gen.add_pdf_screenshots_compact([str(f)], per_page=2)
            else:
                word_gen.add_images_to_page([str(f)], max_per_row=2)

    # ================= 5. 处理差旅补助 (固定项) =================
    print("\n--- 处理差旅补助 ---")

    # 强制添加补助项，无论是否有天数
    subsidy_per_day = config.subsidy_per_day
    subsidy_total = trip_days * subsidy_per_day
    subsidy_amount = subsidy_total if trip_days > 0 else 0
    subsidy_count = trip_days if trip_days > 0 else 0
    subsidy_note = "固定补助" if trip_days > 0 else "固定补助 (请手动填天数)"

    print(f"💰 添加补助项: {subsidy_count}天 * {subsidy_per_day} = ¥{subsidy_amount}")

    item = TravelExpenseItem(
        日期="",
        费用名称="差旅补助",
        单价=subsidy_per_day,
        数量=subsidy_count,  # 为0时 Excel 可能不显示，视模版而定，但这里 logic 是没问题的
        费用金额=subsidy_amount,
        备注=subsidy_note
    )
    updater.add_item(item)

    # ================= 6. 处理差旅补助替票 =================
    if dirs["subsidy"].exists():
        subsidy_files = list(dirs["subsidy"].glob("*"))
        if subsidy_files:
            word_gen.add_section_title("差旅补助替票附件")
            valid_files = [f for f in subsidy_files if f.name.startswith(".") is False]

            # 汇总替票金额
            subsidy_invoice_info = ocr.extract_subsidy_invoice_total(str(dirs["subsidy"]))
            invoice_total = subsidy_invoice_info.get("total_amount", 0)
            invoice_count = subsidy_invoice_info.get("count", 0)
            invoices = subsidy_invoice_info.get("invoices", [])

            print(f"📄 替票发票汇总:")
            for inv in invoices:
                print(f"   - {inv['file']}: ¥{inv['amount']:.2f}")
            print(f"   共 {invoice_count} 张，合计: ¥{invoice_total:.2f}")

            # 验证替票是否足够抵扣补助
            if subsidy_amount > 0:
                if invoice_total >= subsidy_amount:
                    print(f"✅ 替票金额 ¥{invoice_total:.2f} >= 补助金额 ¥{subsidy_amount:.2f}，抵扣完成")
                else:
                    shortfall = subsidy_amount - invoice_total
                    print(f"")
                    print(f"⚠️⚠️⚠️ 替票金额不足！")
                    print(f"   当前抵扣票据金额: ¥{invoice_total:.2f}")
                    print(f"   应抵扣补助金额: ¥{subsidy_amount:.2f}")
                    print(f"   还差: ¥{shortfall:.2f}")
                    print(f"")

            # 将替票放入 Word，不计入 Excel (因为有了固定补助项)
            for f in valid_files:
                if f.suffix.lower() == '.pdf':
                    word_gen.add_pdf_screenshots_compact([str(f)], per_page=2)
                else:
                    word_gen.add_images_to_page([str(f)], max_per_row=2)
    
    # ================= 保存结果 =================
    print("\n💾 保存结果...")

    excel_path = print_dir / template_file.name
    # 强制覆盖旧文件如果存在
    if excel_path.exists():
        os.remove(excel_path)

    saved_excel = updater.update_template(str(excel_path))
    print(f"✅ Excel 已更新: {saved_excel}")
    print(f"   💰 总金额: ¥{updater.total_amount:.2f}")

    word_path = print_dir / "报销材料汇总.docx"
    saved_word = word_gen.save(str(word_path))
    print(f"✅ Word 已生成: {saved_word}")

    # ================= 生成校验报告 =================
    verification_report["items"] = updater.items
    verification_report["summary"] = {
        "total_amount": updater.total_amount,
        "trip_days": trip_days,
        "subsidy_per_day": subsidy_per_day,
        "subsidy_total": subsidy_amount,
    }

    # 保存校验报告
    report_path = print_dir / "校验报告.txt"
    _generate_verification_report(verification_report, str(report_path))
    print(f"📋 校验报告已生成: {report_path}")

    print("\n🎉 处理完成!")

    return verification_report


def _generate_verification_report(report: Dict, output_path: str):
    """
    生成校验报告文件，供人工复核
    :param report: 校验报告数据
    :param output_path: 输出路径
    """
    lines = []
    lines.append("=" * 60)
    lines.append(f"出差报销校验报告 - {report['trip_name']}")
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 60)
    lines.append("")

    # 汇总信息
    summary = report.get("summary", {})
    lines.append("【汇总信息】")
    lines.append(f"  出差天数: {summary.get('trip_days', 0)} 天")
    lines.append(f"  补助单价: ¥{summary.get('subsidy_per_day', 0):.2f}/天")
    lines.append(f"  补助金额: ¥{summary.get('subsidy_total', 0):.2f}")
    lines.append(f"  报销总额: ¥{summary.get('total_amount', 0):.2f}")
    lines.append("")

    # 费用明细
    lines.append("【费用明细 - 请人工核对】")
    lines.append("-" * 60)
    lines.append(f"{'序号':<4} {'日期':<12} {'费用类型':<12} {'金额':>10} {'备注'}")
    lines.append("-" * 60)

    items = report.get("items", [])
    for idx, item in enumerate(items, 1):
        date_str = item.日期 if item.日期 else "-"
        lines.append(f"{idx:<4} {date_str:<12} {item.费用名称:<12} ¥{item.费用金额:>8.2f} {item.备注}")

    lines.append("-" * 60)
    lines.append(f"{'合计':<16} {'':<12} ¥{summary.get('total_amount', 0):>8.2f}")
    lines.append("")

    # 警告信息
    warnings = report.get("warnings", [])
    if warnings:
        lines.append("【警告信息】")
        for warn in warnings:
            lines.append(f"  ⚠️ {warn}")
        lines.append("")

    # 复核说明
    lines.append("【复核要点】")
    lines.append("  1. 核对每笔费用金额是否与原始票据一致")
    lines.append("  2. 核对日期是否正确")
    lines.append("  3. 核对差旅天数是否正确")
    lines.append("  4. 确认替票金额是否足够抵扣补助")
    lines.append("")
    lines.append("=" * 60)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def process_multiple_trips(trips_root: Path, output_dir: Path, config_path: str = None):
    """
    批量处理多个出差文件夹

    :param trips_root: 包含多个出差文件夹的根目录
    :param output_dir: 输出根目录
    :param config_path: 配置文件路径（可选）
    :return: 所有校验报告的列表
    """
    print(f"🔍 扫描出差文件夹: {trips_root}")

    # 查找所有出差文件夹（包含 "01-城际交通" 子目录的视为出差文件夹）
    trip_folders = []
    for item in trips_root.iterdir():
        if item.is_dir() and (item / "01-城际交通").exists():
            trip_folders.append(item)

    if not trip_folders:
        print("❌ 未找到出差文件夹（需包含 '01-城际交通' 子目录）")
        return []

    print(f"📂 发现 {len(trip_folders)} 个出差文件夹:")
    for folder in trip_folders:
        print(f"   - {folder.name}")

    print("\n" + "=" * 60)

    all_reports = []
    for idx, folder in enumerate(trip_folders, 1):
        print(f"\n[{idx}/{len(trip_folders)}] 处理: {folder.name}")
        print("-" * 60)

        try:
            report = process_travel_expense(folder, output_dir, config_path)
            all_reports.append(report)
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            all_reports.append({
                "trip_name": folder.name,
                "error": str(e)
            })

    # 生成汇总报告
    print("\n" + "=" * 60)
    print("📊 批量处理完成汇总:")
    print("-" * 60)

    total_all = 0
    for report in all_reports:
        if "error" in report:
            print(f"  ❌ {report['trip_name']}: 处理失败 - {report['error']}")
        else:
            amount = report.get("summary", {}).get("total_amount", 0)
            total_all += amount
            print(f"  ✅ {report['trip_name']}: ¥{amount:.2f}")

    print("-" * 60)
    print(f"  📈 所有出差报销总额: ¥{total_all:.2f}")

    return all_reports


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="出差报销处理器")
    parser.add_argument("--trip", help="单个出差目录路径")
    parser.add_argument("--batch", help="批量处理：包含多个出差文件夹的根目录")
    parser.add_argument("--out", help="输出根目录", required=True)
    parser.add_argument("--config", help="配置文件路径（可选）")

    args = parser.parse_args()

    if args.batch:
        # 批量处理模式
        process_multiple_trips(Path(args.batch), Path(args.out), args.config)
    elif args.trip:
        # 单次处理模式
        process_travel_expense(Path(args.trip), Path(args.out), args.config)
    else:
        print("❌ 请指定 --trip（单次处理）或 --batch（批量处理）参数")
        parser.print_help()
