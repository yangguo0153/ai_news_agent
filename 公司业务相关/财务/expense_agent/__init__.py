"""
expense_agent 包初始化
"""

from .parser import AttendanceParser, AttendanceRecord
from .config import *

__version__ = "1.0.0"
__all__ = ["AttendanceParser", "AttendanceRecord"]
