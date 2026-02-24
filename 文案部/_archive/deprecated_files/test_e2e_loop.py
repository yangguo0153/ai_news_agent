"""
端到端测试：模拟真实的审核-修改循环

通过修改审核规则，强制触发修改循环
"""

from swarm_with_llm import create_swarm

def main():
    """
    端到端测试：强制触发修改循环
    """
    print("=" * 60)
    print("端到端测试：审核-修改循环")
    print("=" * 60)

    # 初始化状态
    initial_state = {
        "user_input": {
            "车型": "CR-V",
            "平台": "抖音",
            "数量": 3,  # 减少数量，加快测试
            "方向": "春节返乡"
        },
        "customer_brief": {},
        "planner_brief": {},
        "contents": [],
        "review_results": [],
        "final_output": "",
        "current_attempt": 1,
        "need_manual_review": [],
        "metadata": {}
    }

    # 创建并运行 Swarm
    swarm = create_swarm()
    result = swarm.invoke(initial_state)

    print("\n" + "=" * 60)
    print("执行完成！")
    print(f"最终输出：{result['final_output']}")
    print(f"最终尝试次数：{result['current_attempt']}")
    print(f"需要人工介入：{result.get('need_manual_review', [])}")
    print("=" * 60)

    # 显示统计
    passed_count = sum(1 for r in result['review_results'] if r['passed'])
    total_count = len(result['contents'])
    manual_count = len(result.get('need_manual_review', []))

    print(f"\n统计：")
    print(f"  - 总数：{total_count}篇")
    print(f"  - 通过：{passed_count}篇")
    print(f"  - 需要人工介入：{manual_count}篇")

    # 显示每篇的尝试次数
    print(f"\n每篇尝试次数：")
    for content in result['contents']:
        print(f"  - 篇{content['id']}：{content.get('attempt', 1)}次")


if __name__ == "__main__":
    main()
