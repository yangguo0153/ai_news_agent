"""
端到端测试：包含 AskUserQuestion 交互
"""

from swarm_with_llm import create_swarm

def main():
    """
    端到端测试（带交互）
    """
    print("=" * 60)
    print("Agent Swarm 端到端测试（带交互）")
    print("=" * 60)
    print("\n提示：")
    print("  - 在客户经理和策划者阶段会请求确认")
    print("  - 输入 1 确认，2 修改，3 跳过所有确认")
    print("  - 按 Ctrl+C 或直接回车使用默认选项（确认）")
    print("\n" + "=" * 60)

    # 初始化 Shared Context
    initial_state = {
        "user_input": {
            "车型": "CR-V",
            "平台": "抖音",
            "数量": 5,
            "方向": "春节返乡"
        },
        "customer_brief": {},
        "planner_brief": {},
        "contents": [],
        "review_results": [],
        "final_output": "",
        "current_attempt": 1,
        "need_manual_review": [],
        "skip_confirmations": False,
        "metadata": {}
    }

    # 创建并运行 Swarm
    swarm = create_swarm()
    result = swarm.invoke(initial_state)

    print("\n" + "=" * 60)
    print("执行完成！")
    print(f"最终输出：{result['final_output']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
