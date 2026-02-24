"""
测试审核-修改循环功能

测试场景：
1. 全部通过（无循环）
2. 部分不通过（1次修改成功）
3. 超过3次（人工介入）
"""

import sys
from swarm_with_llm import SharedContext, 审核者, route_after_review

def test_scenario_1():
    """测试场景1：全部通过（无循环）"""
    print("\n" + "="*60)
    print("测试场景1：全部通过（无循环）")
    print("="*60)

    state = {
        "contents": [
            {"id": 1, "content": "a" * 300, "persona": "宝妈", "selling_point": "空间", "attempt": 1, "revision_history": []},
            {"id": 2, "content": "b" * 300, "persona": "孝子", "selling_point": "安全", "attempt": 1, "revision_history": []},
        ],
        "review_results": [],
        "current_attempt": 1,
        "need_manual_review": []
    }

    # 审核
    state = 审核者(state)

    # 路由
    next_node = route_after_review(state)

    print(f"\n结果：")
    print(f"  - 下一个节点：{next_node}")
    print(f"  - 当前尝试次数：{state['current_attempt']}")
    print(f"  - 需要人工介入：{state.get('need_manual_review', [])}")

    assert next_node == "输出校订者", "应该直接进入输出校订者"
    assert state['current_attempt'] == 1, "尝试次数应该保持为1"
    print("\n✅ 测试通过")


def test_scenario_2():
    """测试场景2：部分不通过（模拟1次修改成功）"""
    print("\n" + "="*60)
    print("测试场景2：部分不通过（1次修改成功）")
    print("="*60)

    # 第1次审核：2篇字数不足
    state = {
        "contents": [
            {"id": 1, "content": "a" * 200, "persona": "宝妈", "selling_point": "空间", "attempt": 1, "revision_history": []},  # 字数不足
            {"id": 2, "content": "b" * 300, "persona": "孝子", "selling_point": "安全", "attempt": 1, "revision_history": []},  # 通过
            {"id": 3, "content": "c" * 150, "persona": "小夫妻", "selling_point": "空间", "attempt": 1, "revision_history": []},  # 字数不足
        ],
        "review_results": [],
        "current_attempt": 1,
        "need_manual_review": []
    }

    # 第1次审核
    state = 审核者(state)
    next_node = route_after_review(state)

    print(f"\n第1次审核结果：")
    print(f"  - 下一个节点：{next_node}")
    print(f"  - 当前尝试次数：{state['current_attempt']}")
    print(f"  - 不通过的内容：{[r['id'] for r in state['review_results'] if not r['passed']]}")

    assert next_node == "Writer", "应该返回 Writer 修改"
    assert state['current_attempt'] == 2, "尝试次数应该增加到2"

    # 模拟修改后，第2次审核：全部通过
    state['contents'] = [
        {"id": 1, "content": "a" * 300, "persona": "宝妈", "selling_point": "空间", "attempt": 2, "revision_history": [{"attempt": 1, "issues": ["字数不足"], "suggestions": ["增加内容"]}]},
        {"id": 2, "content": "b" * 300, "persona": "孝子", "selling_point": "安全", "attempt": 1, "revision_history": []},
        {"id": 3, "content": "c" * 300, "persona": "小夫妻", "selling_point": "空间", "attempt": 2, "revision_history": [{"attempt": 1, "issues": ["字数不足"], "suggestions": ["增加内容"]}]},
    ]

    state = 审核者(state)
    next_node = route_after_review(state)

    print(f"\n第2次审核结果：")
    print(f"  - 下一个节点：{next_node}")
    print(f"  - 当前尝试次数：{state['current_attempt']}")

    assert next_node == "输出校订者", "应该进入输出校订者"
    assert state['current_attempt'] == 2, "尝试次数应该保持为2"
    print("\n✅ 测试通过")


def test_scenario_3():
    """测试场景3：超过3次（人工介入）"""
    print("\n" + "="*60)
    print("测试场景3：超过3次（人工介入）")
    print("="*60)

    # 模拟已经尝试3次，仍有1篇不通过
    state = {
        "contents": [
            {"id": 1, "content": "a" * 200, "persona": "宝妈", "selling_point": "空间", "attempt": 3, "revision_history": []},  # 持续不通过
            {"id": 2, "content": "b" * 300, "persona": "孝子", "selling_point": "安全", "attempt": 1, "revision_history": []},  # 通过
        ],
        "review_results": [],
        "current_attempt": 3,
        "need_manual_review": []
    }

    # 第3次审核
    state = 审核者(state)
    next_node = route_after_review(state)

    print(f"\n第3次审核结果：")
    print(f"  - 下一个节点：{next_node}")
    print(f"  - 当前尝试次数：{state['current_attempt']}")
    print(f"  - 需要人工介入：{state.get('need_manual_review', [])}")

    assert next_node == "输出校订者", "应该进入输出校订者（人工介入）"
    assert state['current_attempt'] == 3, "尝试次数应该保持为3"
    assert 1 in state['need_manual_review'], "篇1应该被标记为需要人工介入"
    print("\n✅ 测试通过")


if __name__ == "__main__":
    try:
        test_scenario_1()
        test_scenario_2()
        test_scenario_3()

        print("\n" + "="*60)
        print("🎉 所有测试通过！")
        print("="*60)
    except AssertionError as e:
        print(f"\n❌ 测试失败：{e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试出错：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
