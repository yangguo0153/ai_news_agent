"""
OCR 识别模块

用于识别截图和 PDF 中的文字信息。
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
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
        """从图片中提取文字 (使用 tesseract 命令行 + 图像增强)"""
        temp_path = f"{image_path}.processed.jpg"
        try:
            # 1. 图像预处理
            try:
                img = Image.open(image_path)
                # 转灰度
                img = img.convert('L')
                # 二值化 (阈值150)
                threshold = 150
                img = img.point(lambda p: 255 if p > threshold else 0)
                img.save(temp_path)
                target_path = temp_path
            except Exception as e:
                print(f"⚠️ 图像预处理失败: {e}，将使用原图")
                target_path = image_path

            # 2. 调用 Tesseract CLI
            import subprocess
            cmd = ["tesseract", target_path, "stdout", "-l", self.lang, "--psm", "3"] # 默认 PSM 3
            
            # 捕获输出
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            if result.returncode == 0:
                # 尝试解码
                try:
                    return result.stdout.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        return result.stdout.decode('gbk')
                    except:
                        return result.stdout.decode('utf-8', errors='ignore')
            else:
                print(f"⚠️ Tesseract CLI 失败: {result.stderr.decode('utf-8', errors='ignore')}")
                return ""
                
        except Exception as e:
            print(f"⚠️ OCR 子进程错误 {image_path}: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
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
        
        # ... (保持不变) ...
        # (由于 replace_file_content 需要上下文，这里我只更新 extract_text_from_image 和 extract_trip_sheet_info，
        # 但因为 extract_taxi_invoice_info 在中间，我必须小心不要覆盖它。
        # 更好的策略是分别更新，或者只更新 extract_trip_sheet_info 因为它在最后)
        
        # 这里的 ReplacementContent 包含了 extract_text_from_image 和 extract_text_from_pdf 的更新
        # 但我无法同时更新 extract_trip_sheet_info 如果它不连续。
        # 让我也包含 extract_trip_sheet_info
        return info

    # (Skipping extract_taxi_invoice_info and extract_overtime_reason content updates for brevity in this prompt,
    # but I need to target extract_trip_sheet_info specifically or do multiple calls.
    # The user instruction implies updating BOTH.
    # I will modify extract_text_from_image FIRST.)

# (Cancel above thought: I will use replace_file_content just for extract_text_from_image first)

    def extract_trip_sheet_info(self, pdf_path: str) -> TripSheetInfo:
        """从行程单 PDF 中提取行程信息"""
        text = self.extract_text_from_pdf(pdf_path)
        info = TripSheetInfo(raw_text=text)
        
        # 标准化文本: 将所有空白字符替换为单个空格，变成一行
        text_normalized = re.sub(r'\s+', ' ', text)
        
        # 匹配行程日期和时间
        # 格式: MM-DD HH:MM
        date_pattern = r'(\d{2}-\d{2})\s+(\d{2}:\d{2})'
        matches = list(re.finditer(date_pattern, text_normalized))
        
        for i, match in enumerate(matches):
            date_str = match.group(1)
            time_str = match.group(2)
            
            # 推断年份
            try:
                month = int(date_str.split('-')[0])
                year = "2025" if month >= 11 else "2026"
                full_date = f"{year}-{date_str}"
            except:
                continue
            
            # 获取片段 (当前日期 到 下一个日期 之间的文本)
            start_pos = match.end()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text_normalized)
            segment = text_normalized[start_pos:end_pos]
            
            amount = 0.0
            
            # 提取金额: 找段落中所有的浮点数
            # 排除像 1.2km 这样的数字
            decimal_matches = re.findall(r'(\d+\.\d{2})', segment)
            
            if decimal_matches:
                # 倒序检查
                for amt_str in reversed(decimal_matches):
                    try:
                        val = float(amt_str)
                        # 简单的启发式
                        if val > 3: # 至少大于3元
                             amount = val
                             break
                    except:
                        continue
            
            if amount > 0:
                trip = TripDetail(
                    date=full_date,
                    time=time_str,
                    amount=amount,
                    origin="", 
                    destination=""
                )
                info.trips.append(trip)
                info.total_amount += amount
        
        return info
    
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
        
        # 标准化文本 (去除多余空行，但保留行结构以便逐行分析)
        # text_normalized = re.sub(r'\s+', ' ', text) # 不要完全 flatten
        
        lines = text.split('\n')
        
        # 匹配行程日期和时间
        # 滴滴行程单典型行: "1 快车 01-26 14:42 上海 ... 14.62"
        # 格式: MM-DD HH:MM
        date_pattern = r'(\d{2}-\d{2})\s+(\d{2}:\d{2})'
        
        for line in lines:
            # 查找日期时间
            match = re.search(date_pattern, line)
            if match:
                date_str = match.group(1)
                time_str = match.group(2)
                
                # 推断年份
                try:
                    month = int(date_str.split('-')[0])
                    year = "2025" if month >= 11 else "2026"
                    full_date = f"{year}-{date_str}"
                except:
                    continue
                
                # 提取金额（行末通常是金额）
                # 寻找行内的所有浮点数
                # 排除像 1.2km 这样的数字，金额通常是纯数字或带有 元/¥
                amount_matches = re.findall(r'(\d+\.\d{2})', line)
                amount = 0.0
                
                if amount_matches:
                    # 倒序检查，找一个合理的金额
                    for amt_str in reversed(amount_matches):
                        try:
                            val = float(amt_str)
                            # 简单的启发式：金额通常 > 5，且不应该太大（除非长途）
                            # 另外历程通常也是浮点数，如 4.1，但金额通常是最后一个
                            if val > 0:
                                amount = val
                                break
                        except:
                            continue
                
                if amount > 0:
                    trip = TripDetail(
                        date=full_date,
                        time=time_str,
                        amount=amount,
                        origin="", # 暂不提取起终点，因为OCR格式乱
                        destination=""
                    )
                    info.trips.append(trip)
                    info.total_amount += amount
        
        return info

    # ============ 差旅报销扩展方法 ============
    
    def extract_intercity_dates(self, image_path: str) -> Dict:
        """
        从城际交通截图（火车/机票订单）中识别出发和返程日期

        :param image_path: 订单截图路径
        :return: {"departure_date": "2026-01-25", "return_date": "2026-01-29", "raw_text": "..."}
        """
        text = self.extract_text_from_image(image_path)

        result = {
            "departure_date": "",
            "return_date": "",
            "raw_text": text
        }

        # 提取所有日期
        date_patterns = [
            r'(\d{4}年\d{1,2}月\d{1,2}日)',
            r'(\d{4}-\d{1,2}-\d{1,2})',
            r'(\d{4}/\d{1,2}/\d{1,2})',
            r'(\d{1,2}月\d{1,2}日)',
        ]

        all_dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            all_dates.extend(matches)

        # 标准化日期格式
        normalized_dates = [self._normalize_date(d) for d in all_dates]
        unique_dates = sorted(set(d for d in normalized_dates if d))

        if len(unique_dates) >= 2:
            result["departure_date"] = unique_dates[0]
            result["return_date"] = unique_dates[-1]
        elif len(unique_dates) == 1:
            result["departure_date"] = unique_dates[0]

        return result

    def extract_intercity_dates_from_multiple(self, image_paths: List[str]) -> Dict:
        """
        从多张城际交通截图中提取去程和返程日期

        设计思路：
        - 用户可能有两张截图：一张去程订单，一张返程订单
        - 每张截图通常只有一个主要日期
        - 需要从所有截图中找出最早和最晚的日期作为出发和返回日期

        :param image_paths: 订单截图路径列表
        :return: {"departure_date": "2026-01-25", "return_date": "2026-01-29", "trip_days": 5}
        """
        all_dates = []

        for img_path in image_paths:
            text = self.extract_text_from_image(img_path)

            # 提取日期 - 增加更多模式，特别是 "1月25日周日" 格式
            date_patterns = [
                r'(\d{4}年\d{1,2}月\d{1,2}日)',
                r'(\d{4}-\d{1,2}-\d{1,2})',
                r'(\d{4}/\d{1,2}/\d{1,2})',
                r'(\d{1,2}月\d{1,2}日)(?:周[一二三四五六日])?',  # 支持 "1月25日周日"
            ]

            for pattern in date_patterns:
                matches = re.findall(pattern, text)
                for m in matches:
                    normalized = self._normalize_date(m)
                    if normalized:
                        all_dates.append(normalized)

        result = {
            "departure_date": "",
            "return_date": "",
            "trip_days": 0
        }

        if all_dates:
            unique_dates = sorted(set(all_dates))

            if len(unique_dates) >= 2:
                result["departure_date"] = unique_dates[0]
                result["return_date"] = unique_dates[-1]

                # 计算天数（包含首尾两天）
                try:
                    from datetime import datetime
                    d1 = datetime.strptime(unique_dates[0], "%Y-%m-%d")
                    d2 = datetime.strptime(unique_dates[-1], "%Y-%m-%d")
                    result["trip_days"] = (d2 - d1).days + 1
                except Exception:
                    pass

            elif len(unique_dates) == 1:
                result["departure_date"] = unique_dates[0]
                result["trip_days"] = 1

        return result

    def _normalize_date(self, date_str: str) -> str:
        """
        标准化日期格式

        :param date_str: 原始日期字符串
        :return: 标准化的 YYYY-MM-DD 格式
        """
        # 2026年1月25日 -> 2026-01-25
        match = re.match(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date_str)
        if match:
            return f"{match.group(1)}-{int(match.group(2)):02d}-{int(match.group(3)):02d}"

        # 2026/1/25 -> 2026-01-25
        match = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})', date_str)
        if match:
            return f"{match.group(1)}-{int(match.group(2)):02d}-{int(match.group(3)):02d}"

        # 2026-01-25 (已经标准化)
        match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
        if match:
            return f"{match.group(1)}-{int(match.group(2)):02d}-{int(match.group(3)):02d}"

        # 1月25日 -> 2026-01-25 (推断年份)
        match = re.match(r'(\d{1,2})月(\d{1,2})日', date_str)
        if match:
            month = int(match.group(1))
            # 如果月份>=11，可能是去年；否则是今年
            year = "2025" if month >= 11 else "2026"
            return f"{year}-{month:02d}-{int(match.group(2)):02d}"

        return ""
    
    def extract_hotel_invoice(self, pdf_path: str) -> Dict:
        """
        从酒店发票PDF中提取信息
        
        :param pdf_path: 酒店发票PDF路径
        :return: {"date": "2026-01-25", "amount": 296.0, "hotel_name": "美豪丽致", "raw_text": "..."}
        """
        text = self.extract_text_from_pdf(pdf_path)
        
        result = {
            "date": "",
            "amount": 0.0,
            "hotel_name": "",
            "raw_text": text
        }
        
        # 提取金额 (价税合计) - 优先提取小写金额
        # 策略：找到所有 ¥ 开头的金额，取价税合计行的金额（通常是最大的）
        all_amounts = re.findall(r'[¥￥]\s*([\d,]+\.\d{2})', text)

        if all_amounts:
            amounts_float = []
            for amt_str in all_amounts:
                try:
                    amounts_float.append(float(amt_str.replace(',', '')))
                except ValueError:
                    pass

            if amounts_float:
                if '价税合计' in text or '小写' in text:
                    result["amount"] = max(amounts_float)
                else:
                    result["amount"] = amounts_float[0]

        if result["amount"] == 0:
            amount_patterns = [
                r'小写[：:\s]*[¥￥]?\s*([\d,]+\.?\d*)',
                r'合计[：:\s]*[¥￥]?\s*([\d,]+\.?\d*)',
            ]

            for pattern in amount_patterns:
                match = re.search(pattern, text, re.DOTALL)
                if match:
                    amount_str = match.group(1).replace(',', '')
                    try:
                        result["amount"] = float(amount_str)
                        break
                    except ValueError:
                        continue
        
        # 提取日期
        date_patterns = [
            r'(\d{4}年\d{1,2}月\d{1,2}日)',
            r'(\d{4}-\d{1,2}-\d{1,2})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                result["date"] = match.group(1)
                break
        
        # 提取酒店名称 (通常在销售方名称或发票抬头)
        hotel_patterns = [
            r'销售方[：:]\s*(.+?酒店)',
            r'(.+?酒店)',
            r'销售方名称[：:]\s*(.+)',
        ]
        
        for pattern in hotel_patterns:
            match = re.search(pattern, text)
            if match:
                result["hotel_name"] = match.group(1).strip()[:50]
                break
        
        return result
    
    def extract_general_invoice(self, file_path: str) -> Dict:
        """
        从通用发票(餐饮/礼品等)中提取信息
        
        :param file_path: 发票文件路径 (PDF或图片)
        :return: {"date": "2026-01-25", "amount": 348.0, "type": "餐费", "raw_text": "..."}
        """
        # 判断文件类型
        path = Path(file_path)
        if path.suffix.lower() == '.pdf':
            text = self.extract_text_from_pdf(file_path)
        else:
            text = self.extract_text_from_image(file_path)
        
        result = {
            "date": "",
            "amount": 0.0,
            "type": "",
            "raw_text": text
        }
        
        # 提取金额 - 优先提取价税合计（小写）
        # 策略：找到所有 ¥ 开头的金额，取价税合计行的金额（通常是最大的）
        all_amounts = re.findall(r'[¥￥]\s*([\d,]+\.\d{2})', text)

        if all_amounts:
            # 转换为浮点数并找最大值（价税合计通常是最大的金额）
            amounts_float = []
            for amt_str in all_amounts:
                try:
                    amounts_float.append(float(amt_str.replace(',', '')))
                except ValueError:
                    pass

            if amounts_float:
                # 检查是否有 "价税合计" 或 "小写" 关键词，如果有则取最大值
                if '价税合计' in text or '小写' in text:
                    result["amount"] = max(amounts_float)
                else:
                    # 否则取第一个匹配的金额
                    result["amount"] = amounts_float[0]

        # 如果上述方法失败，尝试其他模式
        if result["amount"] == 0:
            amount_patterns = [
                r'合计[：:\s]*[¥￥]?\s*([\d,]+\.?\d*)',
                r'金额[：:\s]*[¥￥]?\s*([\d,]+\.?\d*)',
            ]

            for pattern in amount_patterns:
                match = re.search(pattern, text, re.DOTALL)
                if match:
                    amount_str = match.group(1).replace(',', '')
                    try:
                        result["amount"] = float(amount_str)
                        break
                    except ValueError:
                        continue
        
        # 提取日期
        date_patterns = [
            r'(\d{4}年\d{1,2}月\d{1,2}日)',
            r'(\d{4}-\d{1,2}-\d{1,2})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                result["date"] = match.group(1)
                break
        
        # 推断费用类型
        if "餐" in text or "饮" in text or "食" in text:
            result["type"] = "餐费"
        elif "礼" in text or "商品" in text:
            result["type"] = "礼品"
        elif "咖啡" in text or "茶" in text:
            result["type"] = "饮品"
        else:
            result["type"] = "其他"
        
        return result


    def extract_subsidy_invoice_total(self, folder_path: str) -> Dict:
        """
        从替票文件夹中提取所有发票金额并汇总

        替票文件命名规则通常是金额.pdf，如 "107.98.pdf", "14.9.pdf"
        如果文件名无法提取金额，则尝试OCR识别

        :param folder_path: 替票文件夹路径
        :return: {
            "invoices": [{"file": "107.98.pdf", "amount": 107.98}, ...],
            "total_amount": 660.75,
            "count": 6
        }
        """
        from pathlib import Path

        folder = Path(folder_path)
        result = {
            "invoices": [],
            "total_amount": 0.0,
            "count": 0
        }

        if not folder.exists():
            return result

        # 获取所有PDF文件
        pdf_files = list(folder.glob("*.pdf"))

        for pdf_file in pdf_files:
            if pdf_file.name.startswith("."):
                continue

            amount = 0.0

            # 方案1: 从文件名提取金额
            # 文件名格式: "107.98.pdf", "5.pdf", "18.pdf"
            filename_without_ext = pdf_file.stem
            try:
                # 尝试直接转换为浮点数
                amount = float(filename_without_ext)
            except ValueError:
                # 如果失败，尝试用正则提取
                amount_match = re.search(r'(\d+\.?\d*)', filename_without_ext)
                if amount_match:
                    try:
                        amount = float(amount_match.group(1))
                    except ValueError:
                        pass

            # 方案2: 如果文件名无法提取金额，OCR识别PDF
            if amount <= 0:
                text = self.extract_text_from_pdf(str(pdf_file))
                # 查找金额模式
                amount_patterns = [
                    r'价税合计[（(]小写[）)][：:\s]*[¥￥]?\s*([\d,]+\.?\d*)',
                    r'合计[：:\s]*[¥￥]?\s*([\d,]+\.?\d*)',
                    r'[¥￥]\s*([\d,]+\.\d{2})',
                ]
                for pattern in amount_patterns:
                    match = re.search(pattern, text)
                    if match:
                        try:
                            amount = float(match.group(1).replace(',', ''))
                            break
                        except ValueError:
                            continue

            if amount > 0:
                result["invoices"].append({
                    "file": pdf_file.name,
                    "amount": amount
                })
                result["total_amount"] += amount
                result["count"] += 1

        return result


if __name__ == "__main__":
    # 测试
    ocr = OCREngine()
    print("OCR 引擎初始化完成")
    print(f"Tesseract 可用: {HAS_TESSERACT}")
    print(f"PyMuPDF 可用: {HAS_PYMUPDF}")
