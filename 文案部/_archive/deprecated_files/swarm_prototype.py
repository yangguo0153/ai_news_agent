"""
Agent Swarm 原型 - Content Expansion

架构：@main (Orchestrator) + 5个业务角色
技术栈：LangGraph + Claude Opus
"""

from typing import TypedDict, List, Dict, Annotated
from langgraph.graph import StateGraph, END
import anthropic
import json
import random

# ============================================================================
# Shared Context（所有角色共享的状态）
# ============================================================================

class SharedContext(TypedDict):
    """Shared Context - 所有角色都能读写的共享状态"""

    # 用户输入
    user_input: Dict  # {车型, 平台, 数量, 方向}

    # 客户经理输出
    customer_brief: Dict  # {需求摘要, 侧重点, 目标用户, 核心卖点, 调性}

    # 策划者输出
    planner_brief: Dict  # {传播方向, 话题切入点, assignments[]}

    # Writer 输出
    contents: List[Dict]  # [{id, content, persona, selling_point, attempt}]

    # 审核者输出
    review_results: List[Dict]  # [{id, passed, issues, suggestions}]

    # 输出校订者输出
    final_output: str  # Excel 文件路径

    # 元数据
    metadata: Dict  # {start_time, current_stage, attempts}


# ============================================================================
# 工具函数
# ============================================================================

def load_material(file_path: str) -> str:
    """加载参考材料"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"材料文件未找到：{file_path}"


def random_sample_details(detail_library: List[str], k: int = 3) -> List[str]:
    """从细节库中随机抽取样本"""
    return random.sample(detail_library, min(k, len(detail_library)))


def check_banned_words(content: str) -> List[str]:
    """检查禁用词"""
    banned = ['说实话', '但问题来了', '你看', '首先', '其次', '方面', '不得不说']
    found = [word for word in banned if word in content]
    return found


def count_params(content: str) -> int:
    """统计参数数量"""
    params = ['10气囊', 'ACE车身', '980Mpa', 'Honda SENSING', 'MM理念', '保值率']
    return sum(1 for p in params if p in content)


# ============================================================================
# 业务角色实现
# ============================================================================

def 客户经理(state: SharedContext) -> SharedContext:
    """
    职责：消化需求、与用户确认、输出 customer_brief
    """
    print("\n[客户经理] 开始处理需求...")

    user_input = state["user_input"]

    # 读取参考材料
    material = load_material("02-参考学习-重构版/01-客户经理材料/需求消化模板.md")

    # 生成 customer_brief（简化版，实际应该用 AskUserQuestion）
    customer_brief = {
        "车型": user_input.get("车型", "CR-V"),
        "平台": user_input.get("平台", "抖音"),
        "数量": user_input.get("数量", 5),
        "方向": user_input.get("方向", "春节返乡"),
        "侧重点": "情感共鸣",
        "目标用户": ["宝妈", "孝子", "小夫妻"],
        "核心卖点": ["空间", "安全"],
        "调性": "温和喜庆",
        "特殊要求": "避免直白描述，多用场景暗示"
    }

    state["customer_brief"] = customer_brief
    print(f"[客户经理] 已生成 customer_brief：{json.dumps(customer_brief, ensure_ascii=False, indent=2)}")

    return state


def 策划者(state: SharedContext) -> SharedContext:
    """
    职责：思考传播方向、输出 planner_brief（包含15篇分配表）
    """
    print("\n[策划者] 开始策划传播方向...")

    customer_brief = state["customer_brief"]

    # 读取参考材料
    material = load_material("02-参考学习-重构版/02-策划者材料/传播方向案例库.md")

    # 生成分配表（简化版）
    target_users = customer_brief["目标用户"]
    selling_points = customer_brief["核心卖点"]
    num_contents = customer_brief["数量"]

    assignments = []
    for i in range(num_contents):
        assignments.append({
            "id": i + 1,
            "persona": target_users[i % len(target_users)],
            "selling_point": selling_points[i % len(selling_points)],
            "scene": f"场景{i+1}",
            "style": "温情"
        })

    planner_brief = {
        "传播方向": "春节返乡-情感路线",
        "话题切入点": "回家的路 = 爱的路",
        "assignments": assignments
    }

    state["planner_brief"] = planner_brief
    print(f"[策划者] 已生成 planner_brief，共{len(assignments)}篇分配")

    return state


def Writer(state: SharedContext) -> SharedContext:
    """
    职责：根据分配任务创作内容
    """
    print("\n[Writer] 开始创作内容...")

    planner_brief = state["planner_brief"]
    assignments = planner_brief["assignments"]

    # 读取参考材料
    template = load_material("02-参考学习-重构版/03-Writer材料/结构模板库/春节返乡-情感路线.md")
    detail_library_text = load_material("02-参考学习-重构版/03-Writer材料/内容变量库/细节描写库.md")

    # 简化：提取一些细节样本
    detail_samples = [
        "不用玩后备箱俄罗斯方块",
        "老妈的腊肉、老爸的酒，一样都不落",
        "后备箱盖一关，满满当当的安心",
        "第二排坐三个大人不挤",
        "高速上突然变道的车，系统提前预警"
    ]

    contents = []
    for assignment in assignments:
        # 随机抽取细节
        selected_details = random_sample_details(detail_samples, k=2)

        # 简化：生成模拟内容（实际应该调用 LLM）
        content = f"""每到春节，{assignment['persona']}最期待的就是回家团聚。那种归心似箭的感觉，从腊月二十八就开始了。

以前大包小裹挤火车，{selected_details[0]}，老人家受累孩子哭闹。车厢里人挤人，行李架上塞得满满当当，下车时还得担心东西有没有落下。那种疲惫和焦虑，经历过的人都懂。每次想起来，都觉得心累。

现在开车回家，想走就走，自由自在。CR-V的{assignment['selling_point']}让人安心，{selected_details[1]}。后备箱装满了给父母准备的年货，后排坐着家人，一路上说说笑笑。高速上开着，心里踏实。

平安到家，就是年。这个春节，让CR-V陪你回家，把温暖带回家。"""

        contents.append({
            "id": assignment["id"],
            "content": content,
            "persona": assignment["persona"],
            "selling_point": assignment["selling_point"],
            "attempt": 1
        })

    state["contents"] = contents
    print(f"[Writer] 已创作{len(contents)}篇内容")

    return state


def 审核者(state: SharedContext) -> SharedContext:
    """
    职责：检查内容、生成修改建议、控制循环
    """
    print("\n[审核者] 开始审核内容...")

    contents = state["contents"]

    # 读取参考材料
    rules = load_material("02-参考学习-重构版/04-审核者材料/硬性规则清单.md")

    review_results = []
    for content_item in contents:
        content = content_item["content"]
        issues = []

        # 检查字数
        word_count = len(content)
        if not (250 <= word_count <= 350):
            issues.append(f"字数不符（当前{word_count}字）")

        # 检查禁用词
        banned_found = check_banned_words(content)
        if banned_found:
            issues.append(f"包含禁用词：{', '.join(banned_found)}")

        # 检查参数数量
        param_count = count_params(content)
        if param_count > 2:
            issues.append(f"参数过多（当前{param_count}个）")

        # 判定
        passed = len(issues) == 0

        # 调试信息
        if not passed:
            print(f"  [审核] 篇{content_item['id']} 不通过：{', '.join(issues)}")

        review_results.append({
            "id": content_item["id"],
            "passed": passed,
            "issues": issues,
            "suggestions": [f"修正：{issue}" for issue in issues] if not passed else []
        })

    state["review_results"] = review_results

    passed_count = sum(1 for r in review_results if r["passed"])
    print(f"[审核者] 审核完成：{passed_count}/{len(contents)} 篇通过")

    return state


def 输出校订者(state: SharedContext) -> SharedContext:
    """
    职责：最终校验、输出 Excel
    """
    print("\n[输出校订者] 开始最终校验...")

    contents = state["contents"]
    review_results = state["review_results"]

    # 读取参考材料
    anti_ai_style = load_material("02-参考学习-重构版/05-输出校订者材料/Anti-AI-style特征库.md")

    # 简化：只输出通过的内容到文本文件（实际应该输出 Excel）
    output_file = "output.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=== 内容输出 ===\n\n")
        for content_item, review in zip(contents, review_results):
            if review["passed"]:
                f.write(f"【篇{content_item['id']}】人设：{content_item['persona']} | 卖点：{content_item['selling_point']}\n")
                f.write(f"{content_item['content']}\n")
                f.write(f"字数：{len(content_item['content'])}\n\n")
                f.write("-" * 50 + "\n\n")

    state["final_output"] = output_file
    print(f"[输出校订者] 已输出到：{output_file}")

    return state


# ============================================================================
# @main (Orchestrator) - 流程编排
# ============================================================================

def create_swarm() -> StateGraph:
    """
    创建 Agent Swarm 流程图
    """
    workflow = StateGraph(SharedContext)

    # 添加业务角色节点
    workflow.add_node("客户经理", 客户经理)
    workflow.add_node("策划者", 策划者)
    workflow.add_node("Writer", Writer)
    workflow.add_node("审核者", 审核者)
    workflow.add_node("输出校订者", 输出校订者)

    # 定义流程（@main 的调度逻辑）
    workflow.set_entry_point("客户经理")
    workflow.add_edge("客户经理", "策划者")
    workflow.add_edge("策划者", "Writer")
    workflow.add_edge("Writer", "审核者")

    # 简化：直接进入输出校订者（实际应该有审核-修改循环）
    workflow.add_edge("审核者", "输出校订者")
    workflow.add_edge("输出校订者", END)

    return workflow.compile()


# ============================================================================
# 主程序入口
# ============================================================================

def main():
    """
    主程序入口
    """
    print("=" * 60)
    print("Agent Swarm 原型 - Content Expansion")
    print("=" * 60)

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
