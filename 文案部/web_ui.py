import streamlit as st
import asyncio
from swarm_with_llm import create_swarm
import sys
import io
import pandas as pd
import PyPDF2
import docx

def parse_uploaded_file(uploaded_file):
    name = uploaded_file.name.lower()
    content = ""
    try:
        if name.endswith('.txt') or name.endswith('.md'):
            content = uploaded_file.read().decode("utf-8")
        elif name.endswith('.pdf'):
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    content += text + "\n"
        elif name.endswith('.docx'):
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                content += para.text + "\n"
    except Exception as e:
        st.error(f"解析文件失败: {e}")
    return content

st.set_page_config(page_title="车企文案 Agent Swarm", layout="wide", page_icon="🚗")

st.title("🚗 车企营销文案批量生成 - Agent Swarm")
st.markdown("基于 LangGraph 构建的多智能体系统。包含：客户经理、策划者、Writer、反八股智能审核(LLM)。")

# 初始化 session_state
if 'brief_uploaded' not in st.session_state:
    st.session_state.brief_uploaded = False
if 'brief_content' not in st.session_state:
    st.session_state.brief_content = ""

with st.sidebar:
    st.header("1️⃣ 需求基石输入")
    st.markdown("⚠️ **必须先上传客户原始需求 (Brief) 才可流转**")
    
    uploaded_file = st.file_uploader("上传需求文档 (.txt, .md, .pdf, .docx)", type=['txt', 'md', 'pdf', 'docx'])
    if uploaded_file is not None:
        # 读取文档内容并塞入 session state
        content = parse_uploaded_file(uploaded_file)
        st.session_state.brief_content = content
        st.session_state.brief_uploaded = True
        st.success("✅ 需求文档已解析，解锁后续步骤。")
    else:
        st.session_state.brief_uploaded = False
        st.session_state.brief_content = ""

    st.divider()
    
    if st.session_state.brief_uploaded:
        st.header("2️⃣ 任务参数配置")
        car_model = st.selectbox("车型", ["CR-V", "HRV", "思域", "英仕派"], index=0)
        platform = st.selectbox("投放平台", ["抖音", "今日头条", "小红书"])
        post_count = st.number_input("生成篇数", min_value=1, max_value=10, value=3)
        direction = st.text_input("附加场景方向", value="过年回家满载而归")
        
        start_btn = st.button("🚀 开始生成", type="primary", use_container_width=True)
    else:
        st.info("上传文档后解锁参数配置...")
        start_btn = False

if start_btn:
    initial_state = {
        "user_input": {
            "车型": car_model,
            "平台": platform,
            "数量": post_count,
            "方向": direction,
            "原始需求文档": st.session_state.brief_content
        },
        "customer_brief": {},
        "planner_brief": {},
        "contents": [],
        "review_results": [],
        "final_output": "",
        "current_attempt": 1,
        "need_manual_review": [],
        "skip_confirmations": True,  # Web端默认跳过交互式命令行
        "metadata": {}
    }
    
    st.info("系统正在全力创作中。包含多重 Agent 节点协作（Writer 并发创作 + LLM 重复审查修订），大约需要 1-3 分钟，请耐心等待...")
    
    with st.spinner("Agent Swarm 多智能体团队正在执行任务...(可在后台终端查看详细编排日志)"):
        # 运行 swarm
        swarm = create_swarm()
        result = swarm.invoke(initial_state)
    
    st.success("🎉 生成与审核完毕！")
    
    # 构建 Download Excel 数据容器
    if result.get("review_results"):
        passed_count = sum(1 for r in result.get("review_results", []) if r["passed"])
        st.markdown(f"### 📋 审核控制板: ✅ 已通过，待下载 ({passed_count} / {post_count} 篇)")
        
        # 将结果拼装为 dataframe 以供流式下载
        export_data = []
        for content in result.get("contents", []):
            review_res = next((r for r in result.get("review_results", []) if r["id"] == content["id"]), {})
            export_data.append({
                "编号": content["id"],
                "状态": "通过" if review_res.get("passed") else "需人工介入",
                "人设": content.get("persona", "未提供"),
                "卖点": content.get("selling_point", "未提供"),
                "引子场景": content.get("scene", "未提供"),
                "正文内容": content.get("content", "")
            })
            
        df = pd.DataFrame(export_data)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Agent_Swarm_产出')
        
        st.download_button(
            label="📥 导出 Excel 终稿文件",
            data=buffer.getvalue(),
            file_name=f"Agent_生成报表_{car_model}_{platform}.xlsx",
            mime="application/vnd.ms-excel",
            type="primary"
        )
    
    st.divider()
    st.subheader("📝 获准发布的优质内容池")
    
    for content in result.get("contents", []):
        review_res = next((r for r in result.get("review_results", []) if r["id"] == content["id"]), None)
        status_emoji = "✅ 通过" if review_res and review_res.get("passed") else "⚠️ 人工作业"
        
        with st.expander(f"【{content['persona']}】 × 【{content['selling_point']}】(尝试创作次数: {content.get('attempt', 1)}) - {status_emoji}", expanded=True):
            st.write(content["content"])
            
            st.markdown("---")
            rev_history = content.get("revision_history", [])
            if rev_history:
                st.caption(f"🔧 被打回 {len(rev_history)} 次历史：")
                for i, rev in enumerate(rev_history):
                    st.caption(f"- **第 {rev['attempt']} 次被拒原因**: {', '.join(rev['issues'])}")
            else:
                st.caption("✨ 一遍过！")
