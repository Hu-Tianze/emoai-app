# main.py
import re
import json

# 导入所有模块
from config import client
from state import (
    user_prefs, indexes, emotion_memory, average_emotion, global_tone_and_temp
)
import utils
import emotion_module
import rag_module
import agent_module
import meta_module
import datetime

# --- 在程序启动时，执行一次索引加载 ---
rag_module.load_and_init_indexes()

# 9. 主对话函数 chat_fn()
def chat_fn(user_input, chat_history, tone=0.6, agent_override=None,emotion_history=None):
    if not user_input or not str(user_input).strip():
        yield chat_history, "I'm hearing.", None, ""
        return

    # ==============================================================
    # Meta通道检测：
    # ==============================================================
    meta_mode = False
    meta_key, meta_meaning = meta_module.detect_meta_feedback(user_input)
    if meta_key:
        meta_mode = True
        # (这里是更新 state.user_prefs 的逻辑)
        if "short" in meta_key: user_prefs["reply_length"] = "short"
        elif "long" in meta_key: user_prefs["reply_length"] = "long"
        elif "formal" in meta_key: user_prefs["tone"] = "formal"
        elif "casual" in meta_key: user_prefs["tone"] = "casual"
        print(f"🧭 已检测到Meta反馈：{meta_meaning}，更新偏好 → {user_prefs}")

    # --- 情绪识别 (调用 emotion_module) ---
    prev_val = emotion_history[-1][2] if emotion_history else None
    
    emo, score, adj_val_raw, dimension = emotion_module.detect_emotion(user_input)
    
    emo, adj_val = emotion_module.stable_emotion_fusion(emo, adj_val_raw, score, history=emotion_history, meta_mode=meta_mode)
    
    emotion_history.append((user_input, emo, adj_val))
    
    trend = None
    if len(emotion_history) >= 2:
        diff = emotion_history[-1][2] - emotion_history[-2][2]
        trend = "up" if diff > 0.05 else "down" if diff < -0.05 else "stable"

    # --- 意图识别 (调用 emotion_module) ---
    intent = emotion_module.detect_intent(user_input)

    # --- Agent 路由 (调用 agent_module) ---
    #agent = agent_module.choose_agent_gen3(emo, intent, adj_val, score, prev_val)
    if agent_override and agent_override in agent_module.AGENTS:
        agent = agent_override
        print(f"🤖 Agent override: 使用前端指定的 '{agent}'")
    else:
        agent = agent_module.choose_agent_gen3(emo, intent, adj_val, score, prev_val)
        print(f"🤖 Auto-router: 自动选择 '{agent}'")
        
    # --- RAG 检索 (调用 rag_module, 使用 state.indexes) ---
    if agent == "counselor":
        index, corpus = indexes["counsel_agent"]
        context = rag_module.retrieve_context(index, corpus, user_input, k=3)
        color = "#ADD8E6"
    elif agent == "funny":
        context = ""
        color = "#FFD580"
    else:
        index, corpus = indexes["empathy_agent"]
        context = rag_module.retrieve_context(index, corpus, user_input, k=3)
        color = "#FFB6C1"

    # --- 全局语气/温度 (调用 state 中的函数) ---
    emotion_memory.append({"text": user_input, "emo": emo, "val": adj_val})
    tone_hint, temp = global_tone_and_temp()

    # --- Prompt 构造 (调用 agent_module) ---
    persona = agent_module.build_global_persona(user_prefs)
    # 传 user_input="" 因为 agent_module 不再需要
    agent_instructions = agent_module.build_prompt(agent, context, "", global_tone_hint=tone_hint, prefs=user_prefs)
    
    system_prompt = persona + "\n\n" + agent_instructions

    # 2. 准备发送给 LLM 的消息列表
    messages_for_llm = [{"role": "system", "content": system_prompt}]
    
    # 3. 添加*已有的*对话历史
    messages_for_llm.extend(chat_history) 
        
    # 4. 添加*最新的*用户输入
    messages_for_llm.append({"role": "user", "content": utils.safe_text(user_input)})
    
    chat_history.append({"role":"user","content":user_input})
    chat_history.append({"role":"assistant","content":""}) 
    # --- 流式生成 (使用 config.client) ---
    report_placeholder = f"**Emotion:** {emotion_module.EMOJI_MAP.get(emo,'❔')} {emo} ({score:.2f}) | **Trend:** {trend or '—'} | **Agent:** <span style='color:{color}'>{agent.capitalize()} (Generating...)</span> | **Avg Valence:** {average_emotion():+.2f}"
    yield chat_history, report_placeholder, None, ""

    reply = ""
    try:
        stream = client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=messages_for_llm,
            temperature=temp,
            max_tokens = 200 if user_prefs.get("reply_length") == "short" else 512,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                reply += chunk.choices[0].delta.content
                chat_history[-1]["content"] = reply
                yield chat_history, report_placeholder, None, ""

    except Exception as e:
        reply = f"LLM 调用失败：{e}"
        print(reply)
        chat_history[-1]["content"] = reply # 确保错误信息被设置
        # 即使出错，也应该 yield 一次来结束前端的等待
        # (在 app.py 的 stream 逻辑中已经处理了)
        
        
    # --- 3. 添加日志记录 ---
    try:
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user_input": user_input,
            "emotion": emo, #原始情绪
            "emotion_dimension": dimension, # 六维度标签
            "valence": adj_val, # 情绪值
            "trend": trend,     # 情绪趋势
            "agent_used": agent,
            "ai_reply": reply   # AI 的最终回复
        }
        utils.log_emotion_entry(log_entry)
    except Exception as e:
        print(f"❌ 无法组装日志条目: {e}")
    # --- 日志记录结束 ---
    
    
    # --- 奖励更新 (调用 agent_module) ---
    should_update_reward = False
    #判断是不是针对模型本身的意见
    if not meta_mode:
        if emo.lower() != "neutral":
            if prev_val is None or abs(adj_val - (prev_val or 0)) > 0.05:
                should_update_reward = True
    # ... (奖励更新的判断逻辑) ...
    if should_update_reward:
        last_reply = reply # reply 已经是最终回复了
        agent_module.update_agent_reward(agent, prev_val, adj_val, user_input, last_reply)
    elif meta_mode:
        # --- 情况2: 是 Meta 模式 -> 执行 Meta 反思 ---
        agent_module.update_agent_meta_feedback(agent, user_input, meta_key, meta_meaning)
    else:
        # --- 情况3: 非 Meta 模式，但情绪变化不足 -> 跳过 ---
        print("🧠 情绪奖励: 跳过更新（情绪变化不足）")

    # (这部分在 app.py 的流式输出中处理，main.py 的 chat_fn 只需要在 stream 循环中 yield 即可)
    # ...
    # 流式结束后，app.py 中的 event_stream() 会自动发送 is_final=True 的消息
    # 我们不需要在这里修改 chat_history，因为它在 stream 循环中已经被实时更新了。
    
    # 最后一个 yield 应该在 app.py 的 streaming 循环结束后处理
    # 所以 chat_fn 在 stream 循环结束后就可以正常结束了。
    # app.py 中的代码会处理后续的 final_report
    
    # 确保最终报告被更新 (虽然 app.py 会抓取最后一个 report_placeholder，但我们可以更新它)
    final_report = f"**Emotion:** {emotion_module.EMOJI_MAP.get(emo,'❔')} {emo} ({score:.2f}) | **Trend:** {trend or '—'} | **Agent:** <span style='color:{color}'>{agent.capitalize()}</span> | **Avg Valence:** {average_emotion():+.2f}"
    
    # 在 app.py 中，final_report 是在循环外捕获的。
    # 我们需要确保 stream 循环结束后，chat_fn 不再 yield
    # (原版 emoGen3.py 的 chat_fn 最后有一个 return，在生成器函数中这是不规范的)
    # 我们的流式循环结束后，函数自然退出即可。