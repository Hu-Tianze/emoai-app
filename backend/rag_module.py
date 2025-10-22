# rag_module.py
import numpy as np, pandas as pd, faiss, re, os, json
import kagglehub
from config import client  # 导入 client
from utils import safe_text, safe_batch, chunk_text # 导入工具
from state import indexes # 导入全局 state


def embed_texts(texts, input_type="passage", batch_size=32):
    # TODO: batch_size后期可以调整到64-128提升吞吐
    all_vecs = []
    clean_texts = safe_batch(texts)
    for i in range(0, len(clean_texts), batch_size):
        batch = clean_texts[i:i+batch_size]
        try:
            resp = client.embeddings.create(
                input=batch,
                model="nvidia/llama-3.2-nv-embedqa-1b-v2",
                encoding_format="float",
                extra_body={"input_type": input_type, "truncate": "NONE"}
            )
            all_vecs.extend([d.embedding for d in resp.data])
        except Exception as e:
            print(f"嵌入批次 {i//batch_size+1} 失败：{e}")
    return np.array(all_vecs, dtype="float32")

# ==============================================================
# 4. 构建 FAISS 索引（RAG 检索基础 + 持久化）
# --------------------------------------------------------------
# 功能：
#   - 自动分段 + 嵌入 + 加入向量索引
#   - 如果已有持久化文件，则直接加载，跳过重新嵌入
# ==============================================================

import json

def build_faiss_index(texts, name="empathy", max_chars=1000, overlap=100):
    """
    name: 索引名称（用于保存文件）
    会生成：
        ./faiss_{name}.index
        ./faiss_{name}_corpus.json
    """
    index_path = f"./faiss_{name}.index"
    corpus_path = f"./faiss_{name}_corpus.json"

    # ---------- ① 若已存在持久化文件，则直接加载 ----------
    if os.path.exists(index_path) and os.path.exists(corpus_path):
        try:
            index = faiss.read_index(index_path)
            with open(corpus_path, "r", encoding="utf-8") as f:
                corpus = json.load(f)
            print(f"✅ [{name}] 索引加载完成：{len(corpus)} 段文本，维度 {index.d}（已持久化）")
            return index, corpus
        except Exception as e:
            print(f"⚠️ 无法加载已有索引，重新构建：{e}")

    # ---------- ② 正常构建流程 ----------
    expanded = []
    for t in texts:
        expanded.extend(chunk_text(t, max_chars=max_chars, overlap=overlap))
    corpus = [safe_text(t) for t in expanded if t and t.strip()]
    if not corpus:
        print(f"⚠️ [{name}] 无有效文本，跳过索引构建。")
        return None, []
    print(f"🔧 [{name}] 正在为 {len(corpus)} 段文本生成嵌入...")
    vecs = embed_texts(corpus, input_type="passage")
    if vecs.size == 0:
        print(f"⚠️ [{name}] 未获取到向量，跳过索引构建。")
        return None, []
    dim = vecs.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vecs)
    print(f"✅ [{name}] 索引完成：{len(corpus)} 向量，维度 {dim}（已持久化）")

    # ---------- ③ 保存到当前目录 ----------
    faiss.write_index(index, index_path)
    with open(corpus_path, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)
    print(f"💾 [{name}] 索引与语料已保存至当前目录。")

    return index, corpus


def extract_user_texts(df):
    users = []
    for row in df["empathetic_dialogues"].astype(str):
        m = re.search(r"Customer\s*:\s*(.*?)(?:Agent|$)", row, re.S)
        if m:
            users.append(m.group(1).strip())
    return users

def extract_agent_texts(df):
    agents = []
    for row in df["empathetic_dialogues"].astype(str):
        m = re.search(r"Agent\s*:\s*(.*)", row)
        if m:
            txt = m.group(1).strip()
            if len(txt) > 3:
                agents.append(txt)
    if "labels" in df.columns:
        agents.extend(df["labels"].dropna().astype(str).tolist())
    return agents

def load_datasets_dual():
    # -------- Empathetic Dialogues --------
    path_e = kagglehub.dataset_download("atharvjairath/empathetic-dialogues-facebook-ai")
    df_e = pd.read_csv(f"{path_e}/emotion-emotion_69k.csv")
    df_e = df_e.loc[:, ~df_e.columns.str.contains('^Unnamed')]

    empathy_users = extract_user_texts(df_e)
    empathy_agents = extract_agent_texts(df_e)

    idx_emp_u, corp_emp_u = build_faiss_index(empathy_users[:1500], "empathy_user")
    idx_emp_a, corp_emp_a = build_faiss_index(empathy_agents[:1500], "empathy_agent")

    # -------- CounselChat --------
    path_c = kagglehub.dataset_download("weiting016/counselchat-data")
    df_c = pd.read_csv(f"{path_c}/counselchat-data.csv")
    users = df_c["questionText"].fillna("").astype(str).tolist()
    agents = df_c["answerText"].fillna("").astype(str).tolist()
    idx_con_u, corp_con_u = build_faiss_index(users[:1500], "counsel_user")
    idx_con_a, corp_con_a = build_faiss_index(agents[:1500], "counsel_agent")

    return {
        "empathy_user": (idx_emp_u, corp_emp_u),
        "empathy_agent": (idx_emp_a, corp_emp_a),
        "counsel_user": (idx_con_u, corp_con_u),
        "counsel_agent": (idx_con_a, corp_con_a),
    }
    
def load_and_init_indexes():
    """
    执行一次加载，并把结果存入全局 state.indexes
    这个函数会被 main.py 调用
    """
    try:
        loaded_data = load_datasets_dual()
        indexes.update(loaded_data) # 关键: .update() 会修改从 state 导入的字典
        print("✅ RAG 索引已加载到全局状态。")
    except Exception as e:
        print(f"❌ RAG 索引加载失败: {e}")

# ==============================================================
# 7. 语义检索（RAG）
# --------------------------------------------------------------
# 功能：基于用户query做向量检索，拼接上下文给LLM参考
# ==============================================================
def retrieve_context(index, corpus, query, k=3):
    try:
        if not index or not corpus or not query or not str(query).strip():
            return ""
        clean_query = safe_text(query)[:4000]
        qv = embed_texts([clean_query], input_type="query")
        if qv.size == 0:
            return ""
        D, I = index.search(qv, k)
        ctx = [corpus[i] for i in I[0] if 0 <= i < len(corpus)]
        return "\n\n".join(ctx)
    except Exception as e:
        print(f"检索错误：{e}")
        return ""

# --- 新增一个初始化函数 ---
def load_and_init_indexes():
    """
    执行一次加载，并把结果存入全局 state.indexes
    这个函数应该在 main.py 或 app.py 启动时被调用一次
    """
    loaded_data = load_datasets_dual()
    indexes.update(loaded_data)
    print("✅ RAG 索引已加载到全局状态。")