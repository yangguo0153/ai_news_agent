"""
加班报销自动化 Agent - 启动脚本
"""

import os
import sys

# 切换到脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

# 运行主程序
try:
    from expense_agent.main import main
    main()
except ImportError as e:
    print(f"❌ 启动失败: {e}")
    print("请确保已安装所有依赖:")
    print("pip install -r requirements.txt")
except Exception as e:
    print(f"❌ 运行出错: {e}")
