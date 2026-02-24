"""
发票-行程单匹配器

用于将打车发票与行程单进行匹配
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class InvoiceInfo:
    """发票信息"""
    file_path: str
    total_amount: float = 0.0
    date: str = ""
    city: str = ""  # 开票城市
    raw_text: str = ""


@dataclass
class TripDetail:
    """行程明细"""
    date: str = ""
    time: str = ""
    amount: float = 0.0
    origin: str = ""
    destination: str = ""


def simplify_address(address: str) -> str:
    """
    简化地址，提取核心地名

    例如：
    - "通朝大街|通州区怡乐园一区北机家属区-北1门" -> "怡乐园一区"
    - "丰台区|北京南站(西进站口)" -> "北京南站"
    - "黄渡|雷迪森世嘉酒店(上海嘉定新城同济大学嘉定校区店)" -> "雷迪森世嘉酒店"
    - "嘉定区|汽车·创新港-西北门" -> "创新港"
    - "闵行区|上海虹桥站-南进站口" -> "上海虹桥站"
    """
    if not address:
        return ""

    # 1. 去掉前缀 (区域|)
    if "|" in address:
        address = address.split("|", 1)[-1]

    # 2. 移除常见的区名前缀
    address = re.sub(r'^(通州区|丰台区|朝阳区|海淀区|嘉定区|青浦区|闵行区|安亭镇|黄渡)', '', address)

    # 3. 提取核心地名的优先级规则

    # 规则3a: 火车站/机场 - 保留站名
    station_match = re.search(r'(北京南站|北京西站|北京站|上海虹桥站|上海站|虹桥站|首都机场|大兴机场|浦东机场|虹桥机场)', address)
    if station_match:
        return station_match.group(1)

    # 规则3b: 酒店 - 保留酒店品牌名
    hotel_match = re.search(r'([^\|]+?酒店)', address)
    if hotel_match:
        hotel_name = hotel_match.group(1)
        # 去掉括号里的详细描述
        hotel_name = re.sub(r'\([^)]+\)', '', hotel_name)
        # 只保留品牌名，如 "雷迪森世嘉酒店" 或 "美豪丽致酒店"
        return hotel_name.strip()

    # 规则3c: 小区/园区 - 提取核心名称
    # 匹配 "XXX园/区/城/港" 等
    # 优先匹配常见小区名称格式：XX园X区、XX小区
    community_match = re.search(r'(怡乐园[一二三1-9]区|[\u4e00-\u9fa5]+[一二三四五六七八九十1-9]区)', address)
    if community_match:
        return community_match.group(1)

    place_match = re.search(r'([^\|·\-]*?(?:创新港|产业园|科技园|工业园|园区|小区|新城))', address)
    if place_match:
        place = place_match.group(1)
        # 清理前缀如 "汽车·"
        place = re.sub(r'^汽车[·\.]', '', place)
        # 如果结果为空或太短，取更大的匹配
        if len(place.strip()) < 2:
            # 直接返回 "创新港" 这类简称
            core_match = re.search(r'(创新港|产业园|科技园|工业园)', address)
            if core_match:
                return core_match.group(1)
        return place.strip()

    # 规则3d: 餐厅/店铺 - 保留店名
    shop_match = re.search(r'([^\|]+?(?:店|餐厅|饭店))', address)
    if shop_match:
        shop_name = shop_match.group(1)
        shop_name = re.sub(r'\([^)]+\)', '', shop_name)  # 去括号
        return shop_name.strip()

    # 规则3e: 兜底 - 去掉括号和门牌号等细节
    result = address
    result = re.sub(r'\([^)]+\)', '', result)  # 去括号内容
    result = re.sub(r'[（][^）]+[）]', '', result)  # 去中文括号
    result = re.sub(r'-[东西南北]?\d*门', '', result)  # 去 "-北1门" 等
    result = re.sub(r'-[A-Z]+\d*', '', result)  # 去 "-H2" "-P4停车场" 等
    result = re.sub(r'停车场.*', '', result)  # 去 "停车场" 及之后内容
    result = re.sub(r'进站口.*', '', result)  # 去 "进站口" 及之后内容
    result = re.sub(r'-?\d+号楼.*', '', result)  # 去楼号

    # 如果结果太长(>15字符)，尝试取第一个有意义的词组
    if len(result) > 15:
        # 用常见分隔符分割
        parts = re.split(r'[-·|]', result)
        for part in parts:
            part = part.strip()
            if len(part) >= 2 and len(part) <= 15:
                return part

    return result.strip() if result.strip() else address[:15]


@dataclass
class TripSheetInfo:
    """行程单信息"""
    file_path: str
    trips: List[TripDetail] = field(default_factory=list)
    total_amount: float = 0.0
    city: str = ""  # 行程城市
    raw_text: str = ""


@dataclass
class MatchResult:
    """匹配结果"""
    invoice: InvoiceInfo
    trip_sheet: TripSheetInfo
    trips: List[TripDetail]
    amount_diff: float = 0.0  # 金额差异


class InvoiceMatcher:
    """发票-行程单匹配器"""
    
    def __init__(self, tolerance: float = 0.5):
        """
        :param tolerance: 金额匹配容差（元）
        """
        self.tolerance = tolerance
    
    def match_invoices_to_trips(
        self,
        invoices: List[InvoiceInfo],
        trip_sheets: List[TripSheetInfo]
    ) -> Tuple[List[MatchResult], List[InvoiceInfo], List[TripSheetInfo]]:
        """
        将发票与行程单匹配
        
        匹配规则：
        1. 发票总金额 ≈ 行程单总金额（允许tolerance误差）
        2. 同一城市的发票和行程单优先匹配
        
        :return: (匹配成功列表, 未匹配发票列表, 未匹配行程单列表)
        """
        matched_results = []
        unmatched_invoices = list(invoices)
        unmatched_trip_sheets = list(trip_sheets)
        
        # 按金额排序，从大到小匹配
        unmatched_invoices.sort(key=lambda x: x.total_amount, reverse=True)
        
        for invoice in list(unmatched_invoices):
            best_match = None
            best_diff = float('inf')
            
            for trip_sheet in unmatched_trip_sheets:
                diff = abs(invoice.total_amount - trip_sheet.total_amount)
                
                # 金额差异在容差范围内
                if diff <= self.tolerance:
                    # 优先选择同城市的
                    if invoice.city and trip_sheet.city:
                        if invoice.city == trip_sheet.city and diff < best_diff:
                            best_match = trip_sheet
                            best_diff = diff
                    elif diff < best_diff:
                        best_match = trip_sheet
                        best_diff = diff
            
            if best_match:
                result = MatchResult(
                    invoice=invoice,
                    trip_sheet=best_match,
                    trips=best_match.trips,
                    amount_diff=best_diff
                )
                matched_results.append(result)
                unmatched_invoices.remove(invoice)
                unmatched_trip_sheets.remove(best_match)
        
        # 兜底策略：如果仍有未匹配项，且数量一致，按文件名排序强制匹配（响应用户"顺序要匹配"的要求）
        if unmatched_invoices and unmatched_trip_sheets:
            print(f"⚠️ 启动强制匹配: 剩余发票 {len(unmatched_invoices)} vs 行程单 {len(unmatched_trip_sheets)}")
            
            # 按文件名排序
            unmatched_invoices.sort(key=lambda x: Path(x.file_path).name)
            unmatched_trip_sheets.sort(key=lambda x: Path(x.file_path).name)
            
            # 尽可能匹配
            count = min(len(unmatched_invoices), len(unmatched_trip_sheets))
            forced_matches = []
            
            for i in range(count):
                inv = unmatched_invoices[i]
                ts = unmatched_trip_sheets[i]
                
                print(f"   🔗 强制匹配: {Path(inv.file_path).name} <--> {Path(ts.file_path).name} (Diff: {inv.total_amount - ts.total_amount:.2f})")
                
                result = MatchResult(
                    invoice=inv,
                    trip_sheet=ts,
                    trips=ts.trips,
                    amount_diff=abs(inv.total_amount - ts.total_amount)
                )
                matched_results.append(result)
                forced_matches.append(inv)
            
            # 移除已强制匹配的
            for inv in forced_matches:
                unmatched_invoices.remove(inv)
                # 对应的行程单也要移除（按索引）
                # 这里简单重构 unmatched_trip_sheets
                # 上面的循环 i 是 0..count-1，对应 list 的前 count 个
            unmatched_trip_sheets = unmatched_trip_sheets[count:]
        
        return matched_results, unmatched_invoices, unmatched_trip_sheets
    
    def extract_city_from_text(self, text: str) -> str:
        """从文本中提取城市名"""
        # 常见城市列表
        cities = [
            "北京", "上海", "广州", "深圳", "杭州", "南京", "苏州",
            "成都", "重庆", "武汉", "西安", "天津", "青岛", "厦门",
            "长沙", "郑州", "合肥", "济南", "福州", "昆明", "沈阳"
        ]
        
        for city in cities:
            if city in text:
                return city
        
        return ""


def parse_invoice_pdf(pdf_path: str) -> InvoiceInfo:
    """
    解析打车发票PDF
    
    使用 pdfplumber 提取文本，然后解析金额和日期
    """
    try:
        import pdfplumber
    except ImportError:
        raise ImportError("请安装 pdfplumber: pip install pdfplumber")
    
    info = InvoiceInfo(file_path=pdf_path)
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            info.raw_text = text
            
            # 提取总金额
            # 常见格式: ¥123.45, 金额：123.45, 价税合计 ¥123.45
            amount_patterns = [
                r'价税合计[（(]小写[）)][：:\s]*[¥￥]?\s*([\d,]+\.?\d*)',
                r'合计[：:\s]*[¥￥]?\s*([\d,]+\.?\d*)',
                r'[¥￥]\s*([\d,]+\.\d{2})',
                r'金额[：:]\s*([\d,]+\.?\d*)',
            ]
            
            for pattern in amount_patterns:
                match = re.search(pattern, text)
                if match:
                    amount_str = match.group(1).replace(',', '')
                    try:
                        info.total_amount = float(amount_str)
                        break
                    except ValueError:
                        continue
            
            # 提取日期
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
            
            # 提取城市
            matcher = InvoiceMatcher()
            info.city = matcher.extract_city_from_text(text)
            
    except Exception as e:
        print(f"⚠️ 解析发票失败 {pdf_path}: {e}")
    
    return info


def parse_trip_sheet_pdf(pdf_path: str) -> TripSheetInfo:
    """
    解析行程单PDF

    提取每笔行程的日期、时间、金额、起终点
    使用表格解析获取精确的起点终点，并进行地址简化
    """
    try:
        import pdfplumber
    except ImportError:
        raise ImportError("请安装 pdfplumber: pip install pdfplumber")

    info = TripSheetInfo(file_path=pdf_path)

    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            all_rows = []

            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

                # 尝试提取表格
                tables = page.extract_tables()
                for table in tables:
                    all_rows.extend(table)

            info.raw_text = text

            # 提取城市
            matcher = InvoiceMatcher()
            info.city = matcher.extract_city_from_text(text)

            # 方案1: 优先使用表格数据（更准确）
            if all_rows:
                # 滴滴行程单表头: 序号 车型 上车时间 城市 起点 终点 里程[公里] 金额[元] 备注
                # 索引:           0    1     2       3    4    5     6          7       8
                for row in all_rows:
                    if not row or len(row) < 8:
                        continue

                    # 跳过表头行
                    if row[0] == '序号' or row[0] is None:
                        continue

                    try:
                        # 上车时间格式: "01-26 14:42" 或 "01-26 14:42 周一"
                        time_cell = str(row[2]) if row[2] else ""
                        date_match = re.search(r'(\d{2}-\d{2})\s+(\d{2}:\d{2})', time_cell)

                        if not date_match:
                            continue

                        date_str = date_match.group(1)
                        time_str = date_match.group(2)

                        # 推断年份
                        month = int(date_str.split('-')[0])
                        year = "2025" if month >= 11 else "2026"
                        full_date = f"{year}-{date_str}"

                        # 提取起点终点（索引4和5）
                        origin_raw = str(row[4]) if row[4] else ""
                        dest_raw = str(row[5]) if row[5] else ""

                        # 简化地址
                        origin = simplify_address(origin_raw)
                        destination = simplify_address(dest_raw)

                        # 金额（索引7）
                        amount_str = str(row[7]) if row[7] else "0"
                        amount_str = re.sub(r'[^\d.]', '', amount_str)
                        amount = float(amount_str) if amount_str else 0.0

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

                    except Exception as e:
                        continue

            # 方案2: 如果表格提取失败，回退到文本解析
            if not info.trips:
                text_normalized = re.sub(r'\s+', ' ', text)
                date_pattern = r'(\d{2}-\d{2})\s+(\d{2}:\d{2})'
                matches = list(re.finditer(date_pattern, text_normalized))

                for i, match in enumerate(matches):
                    date_str = match.group(1)
                    time_str = match.group(2)

                    try:
                        month = int(date_str.split('-')[0])
                        year = "2025" if month >= 11 else "2026"
                        full_date = f"{year}-{date_str}"
                    except:
                        continue

                    start_pos = match.end()
                    end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text_normalized)
                    segment = text_normalized[start_pos:end_pos]

                    amount = 0.0
                    origin = ""
                    destination = ""

                    decimal_matches = list(re.finditer(r'(\d+\.\d{2})', segment))
                    if decimal_matches:
                        last_decimal = decimal_matches[-1]
                        try:
                            val = float(last_decimal.group(1))
                            if val > 3:
                                amount = val
                        except:
                            pass

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

    except Exception as e:
        print(f"⚠️ 解析行程单失败 {pdf_path}: {e}")

    return info


if __name__ == "__main__":
    # 测试
    print("发票匹配器模块加载成功")
    
    matcher = InvoiceMatcher()
    print(f"容差设置: {matcher.tolerance}元")
