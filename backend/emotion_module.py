# emotion_module.py
import numpy as np, emoji, re
from transformers import pipeline
from collections import deque
# ==============================================================
# 6. 情绪识别模块
# --------------------------------------------------------------
# 功能：
#   1) 用 RoBERTa 模型识别情绪类型与置信度
#   2) 基于表情符号调整情绪值
#   3) 把情绪标签映射成数值化 valence（[-1,1]）
# ==============================================================

emotion_classifier = pipeline("text-classification",
                              model="j-hartmann/emotion-english-distilroberta-base",
                              top_k=None)

# 表情与标签的情绪值映射表（用于修正）
# VALENCE → 语义强度分数；EMOJI_VALENCE → emoji影响权重
# 范围-1到1
EMOJI_MAP = {
    "joy":"😊","love":"💞","gratitude":"🙏","optimism":"🌤️","admiration":"🌸","caring":"🤗","approval":"👍",
    "pride":"😌","neutral":"😶","realization":"💡","curiosity":"🤔","surprise":"😮","confusion":"😕","remorse":"😔",
    "sadness":"😢","grief":"🕯️","fear":"😱","nervousness":"😬","disappointment":"😞","anger":"😡","disgust":"🤢",
    "embarrassment":"😳","relief":"😮‍💨","amusement":"😄","excitement":"🤩","desire":"💗","annoyance":"😤"
}
VALENCE = {
    "joy":1.0,"love":0.9,"gratitude":0.8,"optimism":0.7,"admiration":0.7,"caring":0.6,"approval":0.5,"pride":0.5,
    "neutral":0.0,"realization":0.2,"curiosity":0.1,"surprise":0.2,"confusion":-0.2,"remorse":-0.6,"sadness":-0.8,
    "grief":-0.9,"fear":-0.9,"nervousness":-0.7,"disappointment":-0.6,"anger":-1.0,"disgust":-0.9,
    "embarrassment":-0.5,"relief":0.4,"amusement":0.8,"excitement":0.9,"desire":0.7,"annoyance":-0.4
}
EMOJI_VALENCE = {"😊":0.8,"😍":0.9,"😄":0.8,"😢":-0.9,"😭":-1.0,"😡":-0.9,"💔":-0.9,"😱":-0.8,"😞":-0.7,"😔":-0.6,"❤️":0.9,"💗":0.8,"🤗":0.7,"🤩":0.8,"😶":0.0,"😕":-0.3,"😮‍💨":0.2}

#六维映射表
SIX_DIMENSIONS_MAP = {
    # happy
    "joy": "happy", "love": "happy", "optimism": "happy", "excitement": "happy",
    "amusement": "happy", "pride": "happy", "relief": "happy", "desire": "happy",
    # satisfied
    "gratitude": "satisfied", "admiration": "satisfied", "approval": "satisfied", "caring": "satisfied",
    # calm
    "neutral": "calm", "realization": "calm", "curiosity": "calm", "surprise": "calm", "confusion": "calm",
    # anxious
    "fear": "anxious", "nervousness": "anxious", "embarrassment": "anxious",
    # angry
    "anger": "angry", "annoyance": "angry", "disgust": "angry",
    # sad
    "sadness": "sad", "grief": "sad", "disappointment": "sad", "remorse": "sad",
}

def emoji_valence_adjust(text, base_val):
    """在文本含emoji时，用表情的平均情绪修正原valence"""
    elist = [ch for ch in text if ch in emoji.EMOJI_DATA]
    if not elist:
        return base_val
    avg = np.mean([EMOJI_VALENCE.get(e, 0) for e in elist])
    return 0.7*base_val + 0.3*avg

def detect_emotion(text):
    """主情绪识别接口：输出(label, score, adjusted_valence,和映射六维情绪)"""
    try:
        results = emotion_classifier(text)[0]
        top = results[0] # 获取置信度最高的情绪
        emo = top['label']
        score = float(top['score'])
        
        base_val = VALENCE.get(emo, 0.0) # 获取基础 valence
        adj_val = emoji_valence_adjust(text, base_val) # 根据 emoji 调整
        
        # --- (新增) 查找六维度标签 ---
        dimension = SIX_DIMENSIONS_MAP.get(emo, "calm") # 默认为 "calm"
        
        # 返回 4 个值
        return emo, score, adj_val, dimension

    except Exception as e:
        print(f"❌ 情绪识别失败: {e}")
        # 出错时也返回 4 个默认值
        return "neutral", 0.0, 0.0, "calm"

def contextual_valence(current_val, history, decay=0.6, clamp=(-1.0, 1.0)):
    """情绪平滑：加入惯性，使情绪变化更自然"""
    #TODO: decay根据后期测试调整 表示情绪平滑率
    if not history:
        return current_val
    prev_val = history[-1][2]
    smoothed = decay * prev_val + (1 - decay) * current_val
    lo, hi = clamp
    return max(lo, min(hi, smoothed))

def detect_intent(text: str) -> str:
    """轻量意图识别：区分 fun/help/ask/chat"""
    # 类似prompt 目前没想到除了hardcode更高效的办法 因为模型理解能力不是特别强
    t = text.lower()
    if re.search(r'\b(joke|funny|laugh|story|meme|pun)\b', t): return "fun"
    if re.search(r'\b(help|advise|problem|issue|cheated|betray(ed)?|divorce|grief|depress(ed)?|anxious|panic|lonely)\b', t): return "help"
    if re.search(r'\b(why|how|what|when|where|which|who)\b', t): return "ask"
    return "chat"

    
def stable_emotion_fusion(emo, val, score, history, meta_mode=False):
    """
    通用情绪继承 + 稳定机制：
    1. 如果当前置信度过低（score < 0.55），继承上一轮情绪；
    2. 如果情绪类别变化过快（joy→anger 或 sadness→neutral），按惯性平滑；
    3. 如果 meta_mode=True，仅轻微调整（不让模型情绪“跳回中性”）；
    4. 针对“meta反馈 + 情绪词”场景，保持上一轮valence不丢失。
    """
    if not history:
        return emo, val

    prev_emo, prev_val = history[-1][1], history[-1][2]
    delta = abs(val - prev_val)

    # --- 模型置信度低：直接继承 ---
    if score < 0.5:
        return prev_emo, prev_val

    # --- 情绪突变（中性/极端跳变） ---
    if delta > 0.6 and np.sign(val) != np.sign(prev_val):
        fused_val = 0.7 * prev_val + 0.3 * val
        fused_emo = prev_emo if abs(prev_val) > abs(val) else emo
        return fused_emo, fused_val

    # --- Meta反馈场景 ---
    # 百分之95来自上轮情绪
    if meta_mode:
        fused_val = 0.95 * prev_val + 0.05 * val
        return prev_emo, fused_val

    # --- 正常衰减平滑 ---
    fused_val = 0.6 * prev_val + 0.4 * val
    return emo, fused_val