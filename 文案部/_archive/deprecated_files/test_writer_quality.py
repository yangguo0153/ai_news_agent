import requests
import json
import time

DEEPSEEK_API_KEY = "sk-208329981b3940e89602e2afe567d227"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def generate_test_copy():
    print("🚀 开始请求 DeepSeek API...")
    
    prompt = """你是一个顶级社交媒体达人，特别擅长在小红书/朋友圈写那种“毫不费力又极具感染力”的真实生活碎片。你现在要写一篇关于【开本田CR-V除夕回家】的动态。

【核心任务】
写一篇大概 200-300 字的短文。
人设：一个刚生完二胎的宝妈。
核心想表达的：后备箱特别大，带娃出门不再焦虑。

【🔴 极其严厉的“去AI味”规则（违反任何一条视为失败）】
1. **绝对禁止**使用任何播音腔、广告腔词汇。
   - 禁用词库：每到春节、归心似箭、说走就走、保驾护航、移动的家、承载、温馨、从容、安全感、车轮滚滚、旅途。
2. **禁止四段式结构**。不要按“起因、经过、结果、升华”来写。就像人发朋友圈一样，想到什么写什么，可以有情绪化的碎碎念。
3. **切口极小**。不要宏大叙事！只聚焦一个极其具体的瞬间（比如：在老家的院子里往下搬东西，或者在高速服务区因为某个小事松了一口气）。
4. **口语化到极致**。多用语气词“太”、“简直”、“哎”、“绝了”、甚至有一些标点符号的不规范（比如连续逗号、没有句号直接换行）。
5. 不要像卖车的一样喊出“本田CR-V”。你可以叫它“我家大白”、“那台老本田”或者就说“刚提的CR-V”。

【优秀的人类写作感觉示例（不要抄，体会这种神经质的真实感）】
- "后备箱塞得像个俄罗斯方块，我妈恨不得把整个菜市场给我搬空...服了，还好这车空间够变态，儿童推车都没折叠直接怼进去了哈~"
- "高速路上老二突然拉了！绝望...赶紧停服务区，把后排座椅一放，直接在车里换尿不湿，空间大就是爽，要换以前那台小破车我可能当场崩溃。"

开始写你的真实碎片（直接输出正文，不要有任何前缀）："""

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9, # 提高多样性和灵气
        "max_tokens": 512
    }

    start_time = time.time()
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        content = result['choices'][0]['message']['content'].strip()
        
        print(f"✅ 生成成功！耗时: {time.time() - start_time:.2f}秒")
        print("\n" + "="*50)
        print(content)
        print("="*50 + "\n")
        
        with open("test_writer_output.txt", "w", encoding="utf-8") as f:
            f.write(content)
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    generate_test_copy()
