"""
测试优化后的 Writer Prompt（使用新材料库）
"""

from swarm_with_llm import load_persona_samples, load_scene_samples, load_detail_library, random_sample_details
import random

def test_prompt_generation():
    """测试 Prompt 生成"""
    print("=" * 60)
    print("测试优化后的 Writer Prompt")
    print("=" * 60)

    # 模拟 assignment
    assignment = {
        "id": 1,
        "persona": "宝妈",
        "selling_point": "空间",
        "scene": "春节场景1"
    }

    # 模拟 customer_brief
    customer_brief = {
        "车型": "CR-V",
        "平台": "抖音",
        "方向": "春节返乡",
        "调性": "温和喜庆"
    }

    # 加载材料库
    print("\n[1] 加载细节库...")
    detail_library_path = "02-参考学习/03-Writer材料/内容变量库/细节描写库.md"
    detail_samples = load_detail_library(detail_library_path)
    selected_details = random_sample_details(detail_samples, k=3)
    print(f"  ✓ 加载了 {len(detail_samples)} 条细节，随机抽取 {len(selected_details)} 条")

    print("\n[2] 加载口吻样本库...")
    persona_samples = load_persona_samples(assignment['persona'])
    persona_opening = random.sample(persona_samples.get("开场切入", [""]), min(2, len(persona_samples.get("开场切入", []))))
    persona_pain = random.sample(persona_samples.get("痛点描述", [""]), min(2, len(persona_samples.get("痛点描述", []))))
    print(f"  ✓ {assignment['persona']}口吻：开场切入 {len(persona_opening)} 条，痛点描述 {len(persona_pain)} 条")

    print("\n[3] 加载场景切入库...")
    scene_samples = load_scene_samples(customer_brief['方向'])
    scene_trigger = random.sample(scene_samples.get("时间触发", [""]), min(2, len(scene_samples.get("时间触发", []))))
    scene_emotion = random.sample(scene_samples.get("情感升华", [""]), min(2, len(scene_samples.get("情感升华", []))))
    print(f"  ✓ {customer_brief['方向']}场景：时间触发 {len(scene_trigger)} 条，情感升华 {len(scene_emotion)} 条")

    # 构建 Prompt
    print("\n[4] 构建 Prompt...")
    prompt = f"""你是一个专业的汽车营销文案创作者。

【任务信息】
- 车型：{customer_brief['车型']}
- 平台：{customer_brief['平台']}（字数：250-350字）
- 方向：{customer_brief['方向']}
- 调性：{customer_brief['调性']}

【本篇分配】
- 人设：{assignment['persona']}
- 卖点：{assignment['selling_point']}
- 场景：{assignment['scene']}

【参考材料 - 学习感觉，不要照抄】

1. 口吻参考（{assignment['persona']}）：
{chr(10).join(f"   - {sample}" for sample in persona_opening[:2]) if persona_opening else "   - （无样本）"}

2. 痛点描述参考：
{chr(10).join(f"   - {sample}" for sample in persona_pain[:2]) if persona_pain else "   - （无样本）"}

3. 场景触发词参考：
{chr(10).join(f"   - {sample}" for sample in scene_trigger[:2]) if scene_trigger else "   - （无样本）"}

4. 情感升华参考：
{chr(10).join(f"   - {sample}" for sample in scene_emotion[:2]) if scene_emotion else "   - （无样本）"}

5. 细节描写参考：
{chr(10).join(f"   - {detail}" for detail in selected_details)}

【创作要求】
1. 结构：4段式
   - 段1：春节场景唤醒（30-50字）
     * 使用时间触发词（每到/一到/每年）
     * 参考"场景触发词"的感觉

   - 段2：以前vs现在对比（80-120字）
     * 以前的痛点 vs 现在开车的便利
     * 参考"痛点描述"的表达方式
     * 融入"细节描写"的具体感受

   - 段3：为什么选CR-V（80-120字）
     * 突出{assignment['selling_point']}卖点
     * 参数≤2个（10气囊、ACE车身、980Mpa、Honda SENSING、MM理念、保值率）
     * 用具体场景说明，而非参数堆砌

   - 段4：情感升华（30-50字）
     * 温和喜庆的收尾
     * 参考"情感升华"的表达方式

2. 字数：250-350字

3. 禁止：
   - 禁用词：说实话、但问题来了、你看、首先、其次、方面、不得不说
   - 直白描述：避免"父母年纪大了，万一遇到紧急情况"
   - 激进表达：避免"智商税""买教训"
   - 参数堆砌：单篇参数不超过2个
   - 照抄样本：学习感觉，用自己的语言重新表达

4. 调性：温和喜庆、场景化、情感共鸣

5. 人设口吻：
   - 宝妈：温柔、细腻、关注孩子和家庭
   - 孝子：成熟、稳重、关注父母安全
   - 小夫妻：轻松、活泼、追求生活品质
   - 职场精英：干练、自信、注重效率

请直接输出文案内容，不要有任何前缀或解释。"""

    print("  ✓ Prompt 构建完成")
    print(f"\n[5] Prompt 预览（前500字符）：")
    print("-" * 60)
    print(prompt[:500] + "...")
    print("-" * 60)

    print(f"\n✓ Prompt 总长度：{len(prompt)} 字符")
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_prompt_generation()
