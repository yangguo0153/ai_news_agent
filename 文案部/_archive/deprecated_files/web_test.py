import asyncio
from swarm_with_llm import create_swarm

def test_run():
    print(f"\n============= 测试 RAG 和动态参数 =============")
    initial_state = {
        "user_input": {
            "车型": "CR-V",
            "平台": "抖音",
            "数量": 1,
            "方向": "日常通勤, 孝敬父母" # 模拟多选
        },
        "customer_brief": {},
        "planner_brief": {},
        "contents": [],
        "review_results": [],
        "final_output": "",
        "current_attempt": 1,
        "need_manual_review": [],
        "skip_confirmations": True,
        "metadata": {}
    }
    swarm = create_swarm()
    result = swarm.invoke(initial_state)
    print("FINISHED")
    for content in result.get("contents", []):
        print(f"\n--- 最终输出 ({len(content['content'])}字) ---")
        print(f"卖点定位: {content['selling_point']}")
        print(f"分配场景: {content['scene']}")
        print("内容正文:")
        print(content['content'])

test_run()
