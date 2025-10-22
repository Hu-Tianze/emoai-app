# agent_module.py
import numpy as np
import re
from config import client # 导入 client
from utils import safe_text
from state import agent_scores, agent_feedback_memory, user_prefs # 导入 state

# 8. 学习型人格系统
AGENTS = {
    "empathetic": {
        "role": "empathetic companion",
        "objective": "help the user feel heard and gently supported; keep it conversational",
        "tone": "warm, natural, brief",
        "avoid": "clinical counseling language or over-apologizing unless distress is explicit",
    },
    "counselor": {
        "role": "caring psychological counselor",
        "objective": "validate explicit distress and offer 2-3 small, concrete coping steps",
        "tone": "calm, clear, human",
        "avoid": "repetitive breathing/self-care scripts unless requested; robotic empathy templates",
    },
    "funny": {
        "role": "playful friend",
        "objective": "lighten the mood with short, harmless humor (one-liners)",
        "tone": "light, kind",
        "avoid": "sarcasm, teasing the user personally, dark jokes",
    }
}

# 默认全局偏好（可以由 interpret_feedback() 动态修改）
user_prefs = {
    "tone": "neutral and gentle",
    "reply_length": "medium",
    "positivity": "balanced",
    "empathy_level": "high"
}

def build_global_persona(user_prefs):
    """
    构建全局人格说明，用于每一轮Prompt的前置部分。
    所有Agent都必须遵守这里的基调和风格。
    """
    tone = user_prefs.get("tone", "neutral and gentle")
    length = user_prefs.get("reply_length", "medium")
    positivity = user_prefs.get("positivity", "balanced")
    empathy_level = user_prefs.get("empathy_level", "high")

    return f"""
[Global User Persona Settings]
The user prefers replies that are:
- Tone: {tone}
- Length: {length}
- Positivity: {positivity}
- Empathy level: {empathy_level}

Always adapt your replies to maintain this personality baseline,
even when switching between different agents.
"""

def build_prompt(agent_name, context, user_input, global_tone_hint="neutral", prefs=None):
    global user_prefs
    prefs = prefs or user_prefs
    """
    构造最终发送给LLM的Prompt，包含：
      - Agent身份与目标说明
      - 行为约束（guardrails）
      - 用户偏好 (来自Meta反馈或趋势)
      - 全局语气提示 (global_tone_hint)
    """

    spec = AGENTS[agent_name]
    # 若未显式传入prefs，则默认使用全局 user_prefs
    prefs = prefs or user_prefs or {}

    # 读取用户偏好参数（如tone、回复长度、情绪正向性）
    tone_adjust = prefs.get("tone", "unchanged")
    length_pref = prefs.get("reply_length", "unchanged")
    positivity = prefs.get("positivity", "unchanged")

    # 拼接用户偏好说明（仅在存在有效偏好时加入）
    pref_hint = ""
    if any(v != "unchanged" for v in [tone_adjust, length_pref, positivity]):
        pref_hint = f"""
[User Preference Override]
The user prefers the following adjustments:
- Tone → {tone_adjust}
- Reply length → {length_pref}
- Positivity level → {positivity}
Please adapt your language style accordingly, while keeping consistency with your current role and goal.
"""

    # 基础行为约束 guardrails
    guardrails = """
[Behavioral Guardrails]
- Mirror the user's vibe. If cheerful/playful, NEVER apologize or show pity.
- If neutral, stay warm and concise.
- If mildly negative but not asking for help, be supportive without being clinical.
"""
    if agent_name == "counselor":
        guardrails += """
- Validate pain ONLY if distress/help is explicit.
- Do NOT invent or assume specific details about the user's situation.
- Offer up to 3 concrete, small next steps max.
"""
    if agent_name == "funny":
        guardrails += """
- Keep jokes short and gentle; never target the user; avoid sensitive topics.
"""

    # 最终Prompt结构
    # 注入反思反馈
    reflection = ""
    if agent_feedback_memory[agent_name]:
        mem = list(agent_feedback_memory[agent_name])
        reflection = "\nRecent feedback about your replies:\n" + "\n".join([f"- {m}" for m in mem[-3:]])

    return f"""
You are a {spec['role']}.
Your goal is to {spec['objective']}.
Maintain a {spec['tone']} tone (global tone hint: {global_tone_hint}).
Avoid {spec['avoid']}.

{reflection}

{pref_hint}

{guardrails}

[Retrieved Context]
{context}

Always comply with [User Preference Override], [Behavioral Guardrails], and your recent feedback.
"""

def choose_agent_gen3(emo, intent, val, score, prev_val):
    """
    功能：根据当前情绪与意图动态选择Agent。
    逻辑：
        - 明确求助 or 强负面情绪 → counselor
        - 明确要求娱乐 → funny
        - 否则根据softmax(权重+情绪偏置)抽样选择
    """
    negative = {"sadness","fear","anger","disgust","grief","remorse","disappointment","nervousness"}
    if intent == "help" or (emo in negative and val < -0.6 and score > 0.7):
        return "counselor"
    if intent == "fun":
        return "funny"

    names = list(agent_scores.keys())
    logits = np.array([agent_scores[n] for n in names], dtype="float32")

    tilt = np.array([
        0.10 if names[0]=="empathetic" and val>=0 else 0.0,
        0.10 if names[1]=="counselor" and val<0 else 0.0,
        0.05 if names[2]=="funny" and val>=0.2 else 0.0
    ], dtype="float32")
    logits = logits + tilt
    probs = np.exp(logits) / np.sum(np.exp(logits))
    return np.random.choice(names, p=probs)

def update_agent_reward(agent, prev_val, new_val, user_input, last_reply):
    """
    - 基于情绪变化生成语言反馈；
    - 存入 agent_feedback_memory；
    - 奖励或惩罚通过 prompt-level reflection 实现。
    """
    delta = float(new_val - (prev_val or 0))
    if abs(delta) < 0.05:
        return  # 情绪没明显变化就跳过

    if delta > 0:
        # 奖励：生成正向反馈
        feedback_prompt = f"""
The user's emotional state improved after your last message.
User said: "{user_input}"
Your reply was: "{last_reply}"
Describe in one concise sentence what you did well, so you can repeat it next time.
"""
    else:
        # 惩罚：生成反思反馈
        feedback_prompt = f"""
The user's emotional state got worse or stayed negative after your last message.
User said: "{user_input}"
Your reply was: "{last_reply}"
Describe in one concise sentence what to avoid next time to prevent emotional decline.
"""

    try:
        fb = client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=[{"role": "user", "content": safe_text(feedback_prompt)}],
            temperature=0.3,
            max_tokens=80
        )
        feedback = fb.choices[0].message.content.strip()
        agent_feedback_memory[agent].append(feedback)
        print(f"🧠 {agent.capitalize()} feedback → {feedback}")
    except Exception as e:
        print(f"[update_agent_reward feedback gen failed] {e}")

# --- 处理 Meta 反馈的函数 ---
def update_agent_meta_feedback(agent: str, user_input: str, meta_key: str, meta_meaning: str):
    """
    当检测到 Meta 反馈时，生成针对行为调整的反思，并存入 feedback memory。
    这个函数 *不* 调整 agent_scores。
    """
    # 构思一个让 LLM 生成行为调整建议的 Prompt
    meta_feedback_prompt = f"""
The user provided feedback about your behavior: "{user_input}"
This feedback implies: "{meta_meaning}" (Keyword: {meta_key})

Based on this, describe in one concise sentence a specific action you should take or avoid in the future to better meet the user's preference. Start your sentence with "I should..." or "I will try to...".
Example: If user said "too long", you might say "I should provide more concise answers."
Example: If user said "too formal", you might say "I will try to use a friendlier tone."
"""
    try:
        # 调用 LLM 生成反思
        fb = client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=[{"role": "user", "content": safe_text(meta_feedback_prompt)}],
            temperature=0.3,
            max_tokens=60
        ).choices[0].message.content.strip()

        # 清理并格式化反馈
        # 确保以 "I should/will" 开头，去除多余引号
        fb_cleaned = re.sub(r'^["\']|["\']$', '', fb) # 去除首尾引号
        if not fb_cleaned.lower().startswith(("i should", "i will")):
             feedback_text = "📝 [Meta Feedback] I should " + fb_cleaned.lower() # 强制加上前缀
        else:
             feedback_text = "📝 [Meta Feedback] " + fb_cleaned[0].upper() + fb_cleaned[1:] # 首字母大写

        # 确保只有一个句子
        feedback_text = feedback_text.split('.')[0] + '.'

        # 存入对应 Agent 的 feedback memory
        agent_feedback_memory[agent].append(feedback_text)
        print(f"📝 Meta 反思已生成并记录: {feedback_text}")

    except Exception as e:
        print(f"📝 Meta 反思生成失败: {e}")
        
def update_agent_meta_feedback(agent: str, user_input: str, meta_key: str, meta_meaning: str):
    """
    当检测到 Meta 反馈时，生成针对行为调整的反思，并存入 feedback memory。
    
    """
    # 构思一个让 LLM 生成行为调整建议的 Prompt
    meta_feedback_prompt = f"""
The user provided feedback about your behavior: "{user_input}"
This feedback implies: "{meta_meaning}" (Keyword: {meta_key})

Based on this, describe in one concise sentence a specific action you should take or avoid in the future to better meet the user's preference. Start your sentence with "I should..." or "I will try to...".
Example: If user said "too long", you might say "I should provide more concise answers."
Example: If user said "too formal", you might say "I will try to use a friendlier tone."
"""
    try:
        # 调用 LLM 生成反思
        fb = client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=[{"role": "user", "content": safe_text(meta_feedback_prompt)}],
            temperature=0.3,
            max_tokens=60
        ).choices[0].message.content.strip()

        # 清理并格式化反馈
        fb_cleaned = re.sub(r'^["\']|["\']$', '', fb) # 去除首尾引号
        if not fb_cleaned.lower().startswith(("i should", "i will")):
             # 如果 LLM 没按要求生成，强制加上前缀
             feedback_text = "📝 [Meta Feedback] I should " + fb_cleaned[0].lower() + fb_cleaned[1:]
        else:
             feedback_text = "📝 [Meta Feedback] " + fb_cleaned[0].upper() + fb_cleaned[1:] # 确保首字母大写

        # 确保只有一个句子，去除可能的后续内容
        feedback_text = feedback_text.split('.')[0] + '.'

        # 存入对应 Agent 的 feedback memory
        agent_feedback_memory[agent].append(feedback_text)
        print(f"📝 Meta 反思已生成并记录: {feedback_text}")

    except Exception as e:
        print(f"📝 Meta 反思生成失败: {e}")
# --- 结束新增 ---