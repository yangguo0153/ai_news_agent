"""
报销自动化 Agent 配置文件

支持加班报销和出差报销两种场景
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# ==================== 加班报销配置 ====================

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


# ==================== 出差报销配置 ====================

@dataclass
class TravelExpenseConfig:
    """出差报销配置"""

    # 差旅补助配置
    subsidy_per_day: float = 150.0  # 每天补助金额（元）

    # 费用类型名称
    expense_names: Dict[str, str] = field(default_factory=lambda: {
        "hotel": "酒店",
        "taxi": "交通费(打车)",
        "meal": "客户餐费",
        "gift": "客户礼品",
        "subsidy": "差旅补助",
    })

    # 文件夹名称映射
    folder_names: Dict[str, str] = field(default_factory=lambda: {
        "intercity": "01-城际交通",
        "taxi": "02-打车",
        "hotel": "03-酒店住宿",
        "general": "04-招待客户类",
        "subsidy": "05-差旅补助替票",
    })

    # Word 排版配置
    word_image_width_full: float = 6.5  # 全宽图片宽度（英寸）
    word_image_width_compact: float = 8.0  # 紧凑模式图片宽度（厘米）
    word_pdf_dpi: int = 150  # PDF 转图片 DPI

    # 备注分隔符
    route_separator: str = "→"  # 起点终点分隔符

    # 年份推断规则
    year_threshold_month: int = 11  # >= 此月份视为上一年

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "TravelExpenseConfig":
        """
        加载配置文件

        :param config_path: 配置文件路径，默认查找当前目录或用户目录下的 config.yaml
        :return: 配置对象
        """
        config = cls()

        if not HAS_YAML:
            return config

        # 查找配置文件
        search_paths = []
        if config_path:
            search_paths.append(Path(config_path))
        else:
            # 默认搜索路径
            search_paths = [
                Path.cwd() / "config.yaml",
                Path.cwd() / "expense_config.yaml",
                Path(__file__).parent / "config.yaml",
                Path.home() / ".expense_agent" / "config.yaml",
            ]

        config_file = None
        for path in search_paths:
            if path.exists():
                config_file = path
                break

        if not config_file:
            return config

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if data:
                # 更新配置
                if "subsidy_per_day" in data:
                    config.subsidy_per_day = float(data["subsidy_per_day"])

                if "expense_names" in data:
                    config.expense_names.update(data["expense_names"])

                if "folder_names" in data:
                    config.folder_names.update(data["folder_names"])

                if "word" in data:
                    word_config = data["word"]
                    if "image_width_full" in word_config:
                        config.word_image_width_full = float(word_config["image_width_full"])
                    if "image_width_compact" in word_config:
                        config.word_image_width_compact = float(word_config["image_width_compact"])
                    if "pdf_dpi" in word_config:
                        config.word_pdf_dpi = int(word_config["pdf_dpi"])

                if "route_separator" in data:
                    config.route_separator = data["route_separator"]

                if "year_threshold_month" in data:
                    config.year_threshold_month = int(data["year_threshold_month"])

            print(f"📋 已加载配置文件: {config_file}")

        except Exception as e:
            print(f"⚠️ 配置文件加载失败: {e}，使用默认配置")

        return config

    def save_template(self, output_path: str):
        """保存配置模板文件"""
        if not HAS_YAML:
            print("⚠️ 需要安装 PyYAML: pip install pyyaml")
            return

        template = {
            "subsidy_per_day": self.subsidy_per_day,
            "route_separator": self.route_separator,
            "expense_names": self.expense_names,
            "folder_names": self.folder_names,
            "word": {
                "image_width_full": self.word_image_width_full,
                "image_width_compact": self.word_image_width_compact,
                "pdf_dpi": self.word_pdf_dpi,
            },
            "year_threshold_month": self.year_threshold_month,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# 出差报销自动化配置文件\n")
            f.write("# 将此文件放在出差材料目录或用户目录 ~/.expense_agent/ 下\n\n")
            yaml.dump(template, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

        print(f"✅ 配置模板已保存: {output_path}")


# 全局默认配置（单例）
_travel_config: Optional[TravelExpenseConfig] = None


def get_travel_config(config_path: Optional[str] = None) -> TravelExpenseConfig:
    """获取出差报销配置（单例模式）"""
    global _travel_config
    if _travel_config is None:
        _travel_config = TravelExpenseConfig.load(config_path)
    return _travel_config


def reset_travel_config():
    """重置配置（用于测试或重新加载）"""
    global _travel_config
    _travel_config = None
