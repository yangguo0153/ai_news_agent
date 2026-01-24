"""
OCR 识别模块

用于识别截图和 PDF 中的文字信息。
"""

import os
import re
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

try:
    import pytesseract
    from PIL import Image
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False


@dataclass
class TaxiInvoiceInfo:
    """打车发票信息"""
    date: str = ""           # 日期
    amount: float = 0.0      # 金额
    origin: str = ""         # 出发地
    destination: str = ""    # 到达地
    raw_text: str = ""       # 原始识别文本


@dataclass
class TripDetail:
    """行程明细"""
    date: str = ""           # 日期 (YYYY-MM-DD)
    time: str = ""           # 时间 (HH:MM)
    amount: float = 0.0      # 金额
    origin: str = ""         # 出发地
    destination: str = ""    # 到达地


@dataclass
class TripSheetInfo:
    """行程单信息"""
    trips: list = None       # 行程明细列表
    total_amount: float = 0.0
    raw_text: str = ""

    def __post_init__(self):
        if self.trips is None:
            self.trips = []


@dataclass
class OvertimeReasonInfo:
    """加班原因信息（从加班申请截图提取）"""
    date: str = ""
    reason: str = ""
    raw_text: str = ""


class OCREngine:
    """OCR 识别引擎"""
    
    def __init__(self, lang: str = "chi_sim+eng"):
        self.lang = lang
        if not HAS_TESSERACT:
            print("⚠️  pytesseract 未安装，OCR 功能受限")
    
    def extract_text_from_image(self, image_path: str) -> str:
        """从图片中提取文字"""
        if not HAS_TESSERACT:
            return ""
        
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang=self.lang)
            return text
        except Exception as e:
            print(f"⚠️  OCR 识别失败 {image_path}: {e}")
            return ""
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """从 PDF 中提取文字"""
        if not HAS_PYMUPDF:
            print("⚠️  PyMuPDF 未安装，无法读取 PDF")
            return ""
        
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            print(f"⚠️  PDF 读取失败 {pdf_path}: {e}")
            return ""
    
    def extract_taxi_invoice_info(self, pdf_path: str) -> TaxiInvoiceInfo:
        """从打车发票 PDF 中提取信息"""
        text = self.extract_text_from_pdf(pdf_path)
        
        info = TaxiInvoiceInfo(raw_text=text)
        
        # 提取日期 (常见格式: 2026年01月20日, 2026-01-20, 2026/01/20)
        date_patterns = [
            r'(\d{4}年\d{1,2}月\d{1,2}日)',
            r'(\d{4}-\d{1,2}-\d{1,2})',
            r'(\d{4}/\d{1,2}/\d{1,2})',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                info.date = match.group(1)
                break
        
        # 提取金额 (常见格式: ¥35.00, 金额: 35.00, 35.00元)
        amount_patterns = [
            r'[¥￥](\d+\.?\d*)',
            r'金额[：:]\s*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*元',
            r'合计[：:]\s*[¥￥]?(\d+\.?\d*)',
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    info.amount = float(match.group(1))
                    break
                except:
                    pass
        
        # 提取出发地和到达地 (常见格式: 从XX到XX, 起点:XX 终点:XX)
        route_patterns = [
            r'从[：:]?\s*(.+?)\s*到[：:]?\s*(.+?)(?:\n|$)',
            r'起点[：:]\s*(.+?)\s*终点[：:]\s*(.+?)(?:\n|$)',
            r'上车[：:]\s*(.+?)\s*下车[：:]\s*(.+?)(?:\n|$)',
        ]
        for pattern in route_patterns:
            match = re.search(pattern, text)
            if match:
                info.origin = match.group(1).strip()[:50]  # 限制长度
                info.destination = match.group(2).strip()[:50]
                break
        
        return info
    

    def extract_overtime_reason(self, image_path: str) -> OvertimeReasonInfo:
        """从加班申请截图中提取加班原因和时间"""
        text = self.extract_text_from_image(image_path)

        info = OvertimeReasonInfo(raw_text=text)

        # 优先提取"开始时间"字段的日期（加班申请截图的核心日期）
        # 格式: "开始时间 2026/1/19 20:00" 或 "开始时间：2026/1/19 20:00"
        start_time_patterns = [
            r'开始时间[：:\s]*(\d{4}/\d{1,2}/\d{1,2})',
            r'开始时间[：:\s]*(\d{4}-\d{1,2}-\d{1,2})',
            r'开始时间[：:\s]*(\d{4}年\d{1,2}月\d{1,2}日)',
        ]
        for pattern in start_time_patterns:
            match = re.search(pattern, text)
            if match:
                info.date = match.group(1)
                break

        # 如果未找到"开始时间"，尝试从"加班日期"表格提取（某些格式的截图）
        # 格式: "加班日期 加班时长(小时)\n2026/1/12 4"
        if not info.date:
            overtime_date_pattern = r'加班日期.*?(\d{4}/\d{1,2}/\d{1,2})'
            match = re.search(overtime_date_pattern, text, re.DOTALL)
            if match:
                info.date = match.group(1)

        # 特殊处理：如果文本包含"开始时间"但标签和值被OCR分开识别了
        # 查找所有日期，排除提交时间的日期，取第一个作为开始时间
        if not info.date and '开始时间' in text:
            # 提取提交时间的日期（用于排除）
            submit_date = None
            submit_match = re.search(r'提交时间.*?(\d{4}/\d{1,2}/\d{1,2})', text, re.DOTALL)
            if submit_match:
                submit_date = submit_match.group(1)

            # 查找所有日期
            all_dates = re.findall(r'(\d{4}/\d{1,2}/\d{1,2})', text)
            for date in all_dates:
                if date != submit_date:
                    info.date = date
                    break

        # 兜底：使用通用日期模式（但跳过"提交时间"的日期）
        if not info.date:
            # 排除"提交时间"行
            lines = text.split('\n')
            filtered_text = '\n'.join(line for line in lines if '提交时间' not in line)

            date_patterns = [
                r'(\d{4}年\d{1,2}月\d{1,2}日)',
                r'(\d{4}-\d{1,2}-\d{1,2})',
                r'(\d{4}/\d{1,2}/\d{1,2})',
                r'(\d{1,2}月\d{1,2}日)',
            ]
            for pattern in date_patterns:
                match = re.search(pattern, filtered_text)
                if match:
                    info.date = match.group(1)
                    break

        # 提取时间 (针对用户反馈只提取起止时间)
        # 常见格式: 18:00 21:00 或 18:00-21:00
        time_matches = re.findall(r'(\d{1,2}:\d{2})', text)
        if len(time_matches) >= 2:
            # 简单假设前两个时间就是起止时间，或者看起来像起止的一对
            # 这里如果不确定，可以不做过多处理，rename逻辑目前只依赖日期
            pass
        
        # 提取加班原因 (保持原有逻辑)
        reason_patterns = [
            r'(?:加班)?原因[：:]\s*(.+?)(?:\n|$)',
            r'事由[：:]\s*(.+?)(?:\n|$)',
            r'备注[：:]\s*(.+?)(?:\n|$)',
            r'申请理由[：:]\s*(.+?)(?:\n|$)',
        ]
        for pattern in reason_patterns:
            match = re.search(pattern, text)
            if match:
                info.reason = match.group(1).strip()[:100]  # 限制长度
                break
        
        if not info.reason:
            lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 10]
            if lines:
                info.reason = lines[0][:100]
        
        return info

    def extract_trip_sheet_info(self, pdf_path: str) -> TripSheetInfo:
        """从行程单 PDF 中提取行程信息"""
        text = self.extract_text_from_pdf(pdf_path)
        info = TripSheetInfo(raw_text=text)
        
        # 标准化文本
        text_normalized = re.sub(r'\s+', ' ', text)
        
        # 匹配行程日期和时间
        # 格式示例: 12-03 02:44 周 三 或 01-12 04:09 周一
        date_pattern = r'(\d{2}-\d{2})\s+(\d{2}:\d{2})\s*周\s*([一二三四五六日])'
        date_matches = list(re.finditer(date_pattern, text_normalized))
        
        for i, match in enumerate(date_matches):
            date_str = match.group(1)
            time_str = match.group(2)
            
            # 推断年份
            month = int(date_str.split('-')[0])
            day = int(date_str.split('-')[1])
            year = "2025" if month >= 12 else "2026"
            full_date = f"{year}-{month:02d}-{day:02d}"
            
            # 获取片段
            start_pos = match.end()
            end_pos = date_matches[i + 1].start() if i + 1 < len(date_matches) else len(text_normalized)
            segment = text_normalized[start_pos:end_pos]
            
            amount = 0.0
            origin = ""
            destination = ""
            
            # 优化金额提取：用户确认金额一定有两位小数，且一般大于20
            # 格式示例: "12.3 34.00" (里程 金额)
            
            # 1. 严格匹配两位小数的金额
            decimal_amounts = re.findall(r'(\d+\.\d{2})', segment)
            if decimal_amounts:
                # 通常是最后一个，但也可能是里程(如 12.50km)
                # 倒序检查
                for amt_str in reversed(decimal_amounts):
                    try:
                        val = float(amt_str)
                        if val >= 20: # 用户确认一般大于20元
                            amount = val
                            break
                    except:
                        continue
            
            # 移除之前的整数匹配逻辑，避免误伤日期的 "6", "7", "8"
            if amount == 0:
                 # 如果完全找不到合规金额，保留为0，后续 excel 生成会处理
                 pass

            # 提取起终点
            # 寻找 "市" 后面的内容，通常包含区名
            city_match = re.search(r'北京\s*市\s*(.+)', segment)
            if city_match:
                addr_content = city_match.group(1).strip()
                
                # 尝试分割起点和终点
                # 终点特征：通常包含 "区|" 或 "区 |"
                # 起点特征：在终点之前
                
                dest_patterns = [
                    r'(.*?)\s+((?:通州|朝阳|海淀|东城|西城|丰台|石景山|顺义|大兴|昌平|房山|门头沟|平谷|密云|怀柔|延庆)区\s*[\|l].+)',
                    r'(.*?)\s+(.*?公司.*?)\s*$'  # 备用：如果终点包含公司
                ]
                
                for dp in dest_patterns:
                    d_match = re.search(dp, addr_content)
                    if d_match:
                        origin = d_match.group(1).strip()
                        destination = d_match.group(2).strip()
                        break
                
                # 保底策略: 如果没分出来，取前一半做起点，后一半做终点(不仅准但比空着强)
                if not origin and not destination:
                     mid = len(addr_content) // 2
                     origin = addr_content[:mid]
                     destination = addr_content[mid:]

            if amount > 0:
                trip = TripDetail(
                    date=full_date,
                    time=time_str,
                    amount=amount,
                    origin=origin,
                    destination=destination
                )
                info.trips.append(trip)
                info.total_amount += amount
        
        return info


if __name__ == "__main__":
    # 测试
    ocr = OCREngine()
    print("OCR 引擎初始化完成")
    print(f"Tesseract 可用: {HAS_TESSERACT}")
    print(f"PyMuPDF 可用: {HAS_PYMUPDF}")
