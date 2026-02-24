"""
测试 AskUserQuestion 交互功能
"""

from swarm_with_llm import ask_user_confirmation

def test_customer_brief_confirmation():
    """测试客户经理阶段的确认"""
    print("\n=== 测试1: 客户需求理解确认 ===")

    customer_brief = {
        "车型": "CR-V",
        "平台": "抖音",
        "数量": "5篇",
        "方向": "春节返乡",
        "侧重点": "情感共鸣",
        "目标用户": "宝妈, 孝子, 小夫妻",
        "核心卖点": "空间, 安全",
        "调性": "温和喜庆",
        "特殊要求": "避免直白描述，多用场景暗示"
    }

    result = ask_user_confirmation(
        title="客户需求理解确认",
        content=customer_brief,
        options=["确认", "修改", "跳过所有确认"]
    )

    print(f"\n✓ 用户选择: {result}")
    return result


def test_planner_brief_confirmation():
    """测试策划者阶段的确认"""
    print("\n=== 测试2: 内容分配表确认 ===")

    planner_brief = {
        "传播方向": "春节返乡-情感路线",
        "话题切入点": "回家的路 = 爱的路",
        "内容分配": [
            "篇1: 宝妈 × 空间 (春节场景1)",
            "篇2: 孝子 × 安全 (春节场景2)",
            "篇3: 小夫妻 × 空间 (春节场景3)",
            "篇4: 宝妈 × 安全 (春节场景4)",
            "篇5: 孝子 × 空间 (春节场景5)"
        ]
    }

    result = ask_user_confirmation(
        title="内容分配表确认",
        content=planner_brief,
        options=["确认", "重新分配", "跳过所有确认"]
    )

    print(f"\n✓ 用户选择: {result}")
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("AskUserQuestion 交互功能测试")
    print("=" * 60)

    # 测试1: 客户经理确认
    result1 = test_customer_brief_confirmation()

    # 测试2: 策划者确认
    result2 = test_planner_brief_confirmation()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print(f"客户经理阶段: {result1}")
    print(f"策划者阶段: {result2}")
