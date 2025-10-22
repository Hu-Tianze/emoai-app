# state.py
# 所有函数共享的全局变量
from collections import deque
import numpy as np


FIXED_SESSION_ID = "main_session"
# 学习变量
agent_scores = {"empathetic": 0.5, "counselor": 0.5, "funny": 0.5}
emotion_memory = deque(maxlen=120) 

# 全局用户偏好
user_prefs = {
    "reply_length": "balanced",
    "tone": "natural",
    "emotion_depth": "medium"
}

# Agent 反馈记忆
agent_feedback_memory = {
    "empathetic": deque(maxlen=5),
    "counselor": deque(maxlen=5),
    "funny": deque(maxlen=5)
}

# RAG 索引 (由 rag_module 加载并填充)
indexes = {} 

# 这个字典将存储所有用户的会话, 格式: {"session_id_1": [...], "session_id_2": [...]}
session_conversations = {
    FIXED_SESSION_ID: []
}
session_emotion_history = {
    FIXED_SESSION_ID: []
}

# --- 依赖 state 的函数 ---

def average_emotion():
    """计算全局平均情绪值"""
    if not emotion_memory:
        return 0.0
    return float(np.mean([m["val"] for m in emotion_memory]))

def global_tone_and_temp():
    """根据全局情绪调节对话温度与语气"""
    avg = average_emotion()
    if avg < -0.4:
        return "extra gentle", 0.2
    if avg > 0.4:
        return "lively", 0.6
    return "neutral", 0.4