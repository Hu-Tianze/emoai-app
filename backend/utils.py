# utils.py
# 通用辅助函数
import re
import json
import datetime
import os
from collections import Counter

LOG_FILE = "emotion_log.jsonl" # 我们将把日志存在这里
# 1. 文本安全处理
def safe_text(text: str) -> str:
    s = re.sub(r"[^\x00-\x7F]+", " ", str(text))
    s = re.sub(r"\s+", " ", s).strip()
    return s

def safe_batch(texts):
    return [safe_text(t) for t in texts if isinstance(t, str) and t.strip()]

# 2. 长文本分段
def chunk_text(text, max_chars=1000, overlap=100):
    clean = safe_text(text)
    if not clean:
        return []
    chunks, start = [], 0
    while start < len(clean):
        end = min(len(clean), start + max_chars)
        chunks.append(clean[start:end])
        start += max_chars - overlap
    return chunks






def log_emotion_entry(log_data: dict):
    """
    将一个字典作为一行 JSON 追加到日志文件中。
    """
    try:
        # 确保有一个时间戳
        if "timestamp" not in log_data:
            log_data["timestamp"] = datetime.datetime.now().isoformat()
        
        # 转换为 JSON 字符串
        log_line = json.dumps(log_data)
        
        # 使用 'a' (追加) 模式写入文件
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
            
    except Exception as e:
        print(f"❌ 情绪日志写入失败: {e}")

def read_emotion_log():
    """
    读取整个 .jsonl 日志文件, 返回一个字典列表。
    """
    if not os.path.exists(LOG_FILE):
        return [] # 如果文件不存在，返回空列表
        
    log_entries = []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip(): # 确保行不为空
                    log_entries.append(json.loads(line))
        return log_entries
    except Exception as e:
        print(f"❌ 情绪日志读取失败: {e}")
        return [] # 出错时返回空
    
    
def get_daily_emotion_distribution():
    """
    读取情绪日志，统计当天的六维度情绪分布。
    返回: 一个包含六个维度 (英文) 计数的字典。
    """
    all_logs = read_emotion_log()
    today_str = datetime.date.today().isoformat()
    
    # 初始化六个维度 (英文) 的计数
    distribution = {
        "happy": 0,
        "satisfied": 0,
        "calm": 0,
        "anxious": 0,
        "angry": 0,
        "sad": 0
    }
    
    # 使用 Counter 来统计今天的情绪维度
    today_dimensions = Counter()
    for entry in all_logs:
        timestamp = entry.get("timestamp", "")
        if timestamp.startswith(today_str): # 检查是否是今天的记录
            dimension = entry.get("emotion_dimension") # 获取六维度标签 (现在是英文)
            if dimension in distribution: # 确保是我们定义的六个维度之一
                today_dimensions[dimension] += 1
                
    # 将 Counter 的结果更新到 distribution 字典中
    distribution.update(today_dimensions)
    
    return distribution