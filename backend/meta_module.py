# meta_module.py
import re, json
from config import client
from utils import safe_text
# 注意：这个模块可能会修改 state.user_prefs
# ==============================================================
# 6.5  元对话通道（Meta-Channel）
# --------------------------------------------------------------
# 功能：
#   - 检测用户是否在对模型进行“反思性”输入
#   - 若检测到：
#       a. 不执行RAG、情绪检测、奖励更新
#       b. 更新 user_prefs 或提供系统解释
# ==============================================================

META_PATTERNS = {
    "shorter": "User prefers shorter replies.",
    "longer": "User prefers longer replies.",
    "too formal": "User prefers a more casual tone.",
    "too casual": "User prefers a more professional tone.",
    "speak slower": "User wants more structured explanations.",
    "more emotional": "User wants richer emotional responses.",
    "less emotional": "User prefers neutral tone.",
}

def detect_meta_feedback(text: str):
    """检测是否为针对模型的meta级反馈"""
    t = text.lower().strip()
    for k, meaning in META_PATTERNS.items():
        if k in t:
            return k, meaning
    if re.search(r"\b(you|your|model|ai|prompt|too long|not human|why you)\b", t):
        return "general_meta", "User is reflecting about the model or its behavior."
    return None, None


# 语义反馈解释模块 (interpret_feedback)
# --------------------------------------------------------------
# 功能：分析用户自然语言反馈（例如 "you talk too much" 或 "please be warmer"）
# 返回 JSON 字典，如 {"reply_length": "short", "tone": "warmer", "positivity": "increase"}
# 该结果将被动态整合进 prompt，让模型理解用户偏好。
# ==============================================================
def interpret_feedback(user_input):
    """
    使用 LLM 解释用户的反馈语义（非显式指令）。
    返回一个字典结构，如 {"reply_length":"short","tone":"warmer"}
    """
    try:
        prompt = f"""
You are a feedback analyzer for a conversational AI system.
The user just said: "{user_input}"
Infer what the user is implicitly asking the chatbot to adjust.

Possible feedback dimensions:
- reply_length: short / long / unchanged
- tone: warmer / calmer / more_humorous / unchanged
- positivity: increase / decrease / unchanged
- empathy: increase / decrease / unchanged

Respond with a short valid JSON object only.
Example: {{"reply_length":"short","tone":"warmer"}}
"""
        resp = client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=[{"role": "user", "content": safe_text(prompt)}],
            temperature=0.2,
            max_tokens=100
        )
        raw = resp.choices[0].message.content.strip()
        # 提取 JSON
        j = re.search(r"\{.*\}", raw, re.S)
        return json.loads(j.group(0)) if j else {}
    except Exception as e:
        print(f"[interpret_feedback] failed: {e}")
        return {}