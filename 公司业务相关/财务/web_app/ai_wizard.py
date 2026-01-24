import re
from typing import List, Any

def suggest_policy_from_chat(message: str) -> dict:
    """
    Simulate an AI extraction of policy settings from natural language.
    Uses Regex for MVP to avoid needing API keys immediately.
    
    Returns a dict with found keys, e.g.:
    {
        "overtime_start_time": "20:00",
        "taxi_daily_limit": 300.0,
        "company_name": "New Corp"
    }
    """
    suggestions = {}
    
    # 1. Extract Overtime Start Time
    if "加班" in message:
        # Match 19:00, 20:30
        hhmm_match = re.search(r'(\d{1,2}:\d{2})', message)
        if hhmm_match:
            suggestions["overtime_start_time"] = hhmm_match.group(1)
        else:
            # Match "8点", "20点"
            hour_match = re.search(r'(\d{1,2})\s*点', message)
            if hour_match:
                hour = int(hour_match.group(1))
                if hour < 12 and ("晚上" in message or "下午" in message):
                    hour += 12
                elif hour < 9:
                    hour += 12
                suggestions["overtime_start_time"] = f"{hour:02d}:00"

    # 2. Extract Taxi Limit
    if "限额" in message or "报销" in message or "打车" in message:
        limit_match = re.search(r'(?:限额|不超过|上限|最多)\s*(\d+)', message)
        if limit_match:
            suggestions["taxi_daily_limit"] = float(limit_match.group(1))
        else:
            yuan_match = re.search(r'(\d+)\s*元', message)
            if yuan_match:
                suggestions["taxi_daily_limit"] = float(yuan_match.group(1))
                 
    # 3. Extract Company Name
    company_match = re.search(r'(?:我们|公司)(?:名|名称)?(?:是|叫|为|设置为)\s*([A-Za-z0-9\u4e00-\u9fa5]+)(?:公司)?', message)
    if not company_match:
        company_match = re.search(r'我是([A-Za-z0-9\u4e00-\u9fa5]+)公司的', message)
    if company_match:
        suggestions["company_name"] = company_match.group(1)

    return suggestions


def detect_template_selection(message: str, templates: List[Any]) -> dict:
    """
    Detect if user is trying to select a workflow template.
    Returns {"selected_template": template_obj} if match found.
    """
    message_lower = message.lower()
    
    # Check for template selection keywords
    selection_keywords = ["选择", "用", "使用", "选", "我要", "帮我"]
    has_selection_intent = any(kw in message for kw in selection_keywords)
    
    if has_selection_intent:
        for tpl in templates:
            # Match by template name
            if tpl.name in message:
                return {"selected_template": tpl}
            # Match by keywords in template name
            if "加班" in message and "加班" in tpl.name:
                return {"selected_template": tpl}
            if "出差" in message and "出差" in tpl.name:
                return {"selected_template": tpl}
    
    return {}


def get_ai_response(message: str, templates: List[Any] = None) -> dict:
    """
    Returns text response and structured data updates.
    Now supports workflow template awareness.
    """
    if templates is None:
        templates = []
    
    updates = suggest_policy_from_chat(message)
    template_result = detect_template_selection(message, templates)
    
    # Check for greeting or help request
    greeting_keywords = ["你好", "hi", "hello", "帮我", "怎么", "如何"]
    is_greeting = any(kw in message.lower() for kw in greeting_keywords)
    
    # Check for template list request
    list_keywords = ["有哪些", "什么流程", "什么方案", "列出", "查看"]
    wants_list = any(kw in message for kw in list_keywords)
    
    # Response Generation
    if wants_list and templates:
        template_list = "\n".join([f"• **{t.name}**: {t.description}" for t in templates])
        response_text = f"目前支持以下报销流程：\n{template_list}\n\n请告诉我您想使用哪个流程?"
        return {"text": response_text, "updates": {}, "action": "list_templates"}
    
    if template_result.get("selected_template"):
        tpl = template_result["selected_template"]
        response_text = f"好的，已为您选择【{tpl.name}】流程。\n\n📋 需要上传的材料：{', '.join(tpl.required_files)}\n\n请在左侧上传文件后点击'开始处理'。"
        updates["selected_workflow"] = tpl.name
        return {"text": response_text, "updates": updates, "action": "select_template"}
    
    if is_greeting and not updates:
        available = ", ".join([t.name for t in templates]) if templates else "加班打车报销"
        response_text = f"你好！我是报销助手 🤖\n\n我可以帮你：\n1. 配置报销规则（如加班起算时间、打车限额）\n2. 选择报销流程（目前支持：{available}）\n\n请告诉我您的需求，例如：\n• '我们公司晚上8点后算加班，限额200元'\n• '我要用加班打车报销流程'"
        return {"text": response_text, "updates": {}, "action": "greeting"}
    
    # Default: Settings extraction
    
    if updates:
        response_text = "已为您更新设置："
        if "company_name" in updates:
            response_text += f"\n- 公司名称：{updates['company_name']}"
        if "overtime_start_time" in updates:
            response_text += f"\n- 加班起算：{updates['overtime_start_time']}"
        if "taxi_daily_limit" in updates:
            response_text += f"\n- 打车限额：{updates['taxi_daily_limit']}元"
    else:
        response_text = "我是您的报销规则配置助手。您可以直接告诉我规则，例如：'加班如果是晚上9点以后，打车限额200元'。"
        
    return {
        "response": response_text,
        "updates": updates,
        "selected_template_id": None
    }

def call_llm_for_intake(message: str, templates: List[Any], settings: Any) -> dict:
    """Call OpenAI compatible API for intent analysis"""
    import requests
    import json
    
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json"
    }
    
    # Construct context from templates
    templates_context = []
    for t in templates:
        templates_context.append({
            "id": t.id,
            "name": t.name,
            "desc": t.description
        })
        
    system_prompt = f"""
    You are a Reimbursement Assistant.
    Goal: Identify which reimbursement scenario matches the user's input.
    Available Templates: {json.dumps(templates_context, ensure_ascii=False)}
    
    Return JSON format only:
    {{
        "matched_template_id": int or null,
        "reasoning": "short explanation",
        "response_to_user": "Friendly response confirming the scenario and asking to proceed. Mention specific required files based on template description."
    }}
    If no match, ask determining questions.
    """
    
    payload = {
        "model": settings.model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ],
        "temperature": 0.3
    }
    
    try:
        response = requests.post(f"{settings.openai_base_url}/chat/completions", headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            # Try parsing JSON
            try:
                # Find JSON block if wrapped in markdown
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                ai_data = json.loads(content.strip())
                return {
                    "matched_template_id": ai_data.get("matched_template_id"),
                    "template_name": next((t.name for t in templates if t.id == ai_data.get("matched_template_id")), ""),
                    "message": ai_data.get("response_to_user")
                }
            except:
                print(f"Failed to parse LLM JSON: {content}")
    except Exception as e:
        print(f"LLM Request Failed: {e}")
        
    raise Exception("LLM processing failed")


def analyze_intake_intent(message: str, templates: List[Any], settings: Any = None) -> dict:
    """
    Analyzes user message to determine which reimbursement template matches.
    Uses LLM if configured, otherwise falls back to Regex.
    """
    import json
    
    # 1. Try LLM if configured
    if settings and settings.openai_api_key:
        try:
            return call_llm_for_intake(message, templates, settings)
        except Exception as e:
            print(f"Falling back to Regex due to LLM error: {e}")
            
    # 2. Regex Fallback
    for tpl in templates:
        # Simple keyword matching
        keywords = []
        if "加班" in tpl.name: keywords.extend(["加班", "打车", "晚归", "出租", "滴滴"])
        if "出差" in tpl.name: keywords.extend(["出差", "差旅", "机票", "酒店", "火车", "高铁"])
        
        if any(kw in message for kw in keywords):
             req_files = json.loads(tpl.required_files_json) if hasattr(tpl, 'required_files_json') else []
             return {
                "matched_template_id": tpl.id,
                "template_name": tpl.name,
                "message": f"好的，这属于【{tpl.name}】场景。\n根据规定，您需要准备以下材料：\n" + "\n".join([f"- {f}" for f in req_files]) + "\n\n准备好了吗？"
            }
            
    # 3. No match found
    return {
        "matched_template_id": None,
        "template_name": None,
        "message": "抱歉，我没能确认识别您的场景。目前支持：\n" + "\n".join([f"- {t.name}" for t in templates]) + "\n\n请再详细描述一下？"
    }
