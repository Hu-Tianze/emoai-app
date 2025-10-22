# EmoAI: 情绪感知型多Agent聊天机器人 (详细功能文档)

`EmoAI` 是一个先进的、具备情绪感知能力的聊天机器人项目。它不仅能理解用户在说什么，还能分析用户的情绪，并动态切换不同的“AI人格”（Agents）来提供最合适的回应。

本文档将详细拆解项目中的每一个文件及其包含的核心功能。

## 目录

1.  **`app.py`** - API 服务器入口
2.  **`main.py`** - 核心业务逻辑编排
3.  **`config.py`** - API 客户端配置
4.  **`state.py`** - 全局状态管理
5.  **`emotion_module.py`** - 情绪与意图分析
6.  **`agent_module.py`** - Agent 人格与路由
7.  **`rag_module.py`** - RAG 检索模块
8.  **`meta_module.py`** - 元反馈处理
9.  **`utils.py`** - 通用工具函数

---

## 1. `app.py` - API 服务器入口

**文件职责**: 使用 `FastAPI` 框架构建 Web 服务器，暴露与前端交互的 API 接口。

### 核心功能与 API 端点

* **`app = FastAPI(title="EmoAI API")`**
    * 初始化 FastAPI 应用实例。

* **`@app.post("/api/chat/stream")`**
    * **功能**: 核心的流式聊天接口。这是前端发送用户输入并接收 AI 回答的主要端点。
    * **`chat_stream(request: Request)`**
        * **接收**: 接收来自前端的 JSON 请求，包含 `user_input` (用户输入)，以及可选的 `agent_override` (强制指定 Agent)。
        * **状态管理**: 从 `state.py` 模块获取固定会话 ID (`FIXED_SESSION_ID`) 对应的聊天历史 (`chat_history_session`) 和情绪历史 (`emotion_history_session`)。
        * **调用核心逻辑**: 将所有参数传递给 `main.py` 中的 `chat_fn` 函数。
        * **`event_stream()` (异步生成器)**:
            * **流式响应**: 循环遍历 `chat_fn` 返回的 `yield` 数据（即AI生成的文本块）。
            * **格式化**: 将每个文本块打包成 `Server-Sent Events (SSE)` 格式（`data: {...}\n\n`）。
            * **发送报告**: 在数据流的最后，发送一个包含 `is_final: true` 和 `report` (分析报告) 的 JSON 对象，通知前端数据流结束。
        * **返回**: 返回一个 `StreamingResponse` 对象，实现流式响应。

* **`@app.get("/api/emotion_log")`**
    * **功能**: 情绪日志读取接口。
    * **`get_emotion_log()`**: 调用 `utils.read_emotion_log()`，获取 `emotion_log.jsonl` 文件中的所有日志条目，并按时间倒序后返回。

* **`@app.get("/api/daily_emotion_distribution")`**
    * **功能**: 当日情绪分布统计接口。
    * **`get_daily_distribution()`**: 调用 `utils.get_daily_emotion_distribution()`，获取并返回一个字典，统计当天用户在六个主要情绪维度上的分布情况。

* **`if __name__ == "__main__":`**
    * **功能**: 允许通过 `python app.py` 直接启动 `uvicorn` 服务器。

---

## 2. `main.py` - 核心业务逻辑编排

**文件职责**: 项目的“大脑”。`chat_fn` 函数是所有模块的调度中心，它定义了处理用户输入的完整流程（Pipeline）。

### 核心功能

* **`rag_module.load_and_init_indexes()`**
    * 在程序启动时首先被调用，执行一次RAG索引的加载，将数据填充到 `state.indexes` 中。

* **`chat_fn(user_input, chat_history, ...)`**
    * **功能**: 核心对话处理函数，是一个生成器 (Generator)，用于流式返回响应。
    * **执行流程**:
        1.  **Meta通道检测**: 调用 `meta_module.detect_meta_feedback(user_input)`。如果检测到元反馈（如 "you are too formal"），则设置 `meta_mode = True`，并**立即更新** `state.user_prefs` 中的偏好（如 `reply_length`）。
        2.  **情绪识别**: 调用 `emotion_module.detect_emotion(user_input)` 获取原始情绪。
        3.  **情绪平滑**: 调用 `emotion_module.stable_emotion_fusion()`，结合历史情绪，防止情绪突变。
        4.  **意图识别**: 调用 `emotion_module.detect_intent(user_input)` (例如 "help", "fun", "chat")。
        5.  **Agent 路由**:
            * 检查是否存在 `agent_override`。
            * 如果不存在，则调用 `agent_module.choose_agent_gen3()`，根据情绪、意图和Agent得分自动选择一个Agent (如 "empathetic", "counselor")。
        6.  **RAG 检索**:
            * 根据选择的 Agent，从 `state.indexes` 中选取对应的索引。
            * 调用 `rag_module.retrieve_context()` 检索相关知识片段作为 `context`。
            * (例如, "counselor" 使用 `counsel_agent` 索引，"funny" 则跳过RAG)。
        7.  **动态Prompt构建**:
            * 调用 `agent_module.build_global_persona(user_prefs)` 获取基于用户偏好的全局人格。
            * 调用 `agent_module.build_prompt()` 构建特定于Agent的、包含RAG上下文和行为约束的最终Prompt。
        8.  **LLM 调用 (流式)**:
            * 使用 `config.client` 调用NVIDIA API (`meta/llama-3.1-8b-instruct`)，设置 `stream=True`。
            * 循环遍历API返回的 `chunk`，`yield` (返回) 给 `app.py`。
        9.  **生成分析报告**: 在流式结束后，生成一个包含情绪、Agent、RAG状态等信息的 `report_str`。
        10. **日志记录**: 调用 `utils.log_emotion_entry()`，将整轮对话（输入、情绪、Agent、AI回复等）存入 `emotion_log.jsonl`。
        11. **Agent 奖励/反思**:
            * 如果**不是** `meta_mode` 且情绪变化显著，调用 `agent_module.update_agent_reward()`，根据情绪变化（变好或变差）来奖励或惩罚当前Agent。
            * 如果**是** `meta_mode`，则调用 `agent_module.update_agent_meta_feedback()`，让LLM反思用户的反馈，并将反思结果存入Agent的记忆中。

---

## 3. `config.py` - API 客户端配置

**文件职责**: 初始化并配置与NVIDIA API通信的全局客户端。

* **`NV_API_KEY = os.getenv(...)`**
    * 从环境变量 `NV_API_KEY` 中读取NVIDIA API密钥。如果未设置，则使用一个硬编码的默认值。
* **`client = OpenAI(...)`**
    * 使用 `openai` 库初始化一个 `OpenAI` 客户端实例。
    * `api_key` 设置为 `NV_API_KEY`。
    * `base_url` 设置为NVIDIA的API端点 `https://integrate.api.nvidia.com/v1`。
    * 这个 `client` 变量会被 `agent_module`, `rag_module`, `meta_module` 等所有需要调用LLM或嵌入模型的模块导入和使用。

---

## 4. `state.py` - 全局状态管理

**文件职责**: 定义项目运行期间所有模块共享的全局变量和状态。这使得状态（如用户偏好、会话历史）可以在不同的API请求之间保持持久。

### 核心变量

* **`FIXED_SESSION_ID = "main_session"`**
    * 定义一个固定的会话ID，用于在 `app.py` 中索引会话历史，使应用表现为单用户模式。
* **`agent_scores = {"empathetic": ..., "counselor": ..., "funny": ...}`**
    * 存储三个Agent的当前得分。这个得分由 `agent_module.update_agent_reward()` 修改，并由 `agent_module.choose_agent_gen3()` 读取，影响Agent的选择概率。
* **`emotion_memory = deque(maxlen=120)`**
    * 一个固定长度的队列，存储最近120次的情绪记录，用于计算长期平均情绪。
* **`user_prefs = {...}`**
    * 存储全局用户偏好（如 `reply_length`, `tone`）。这个字典会被 `meta_module` 和 `main.py` 修改，并被 `agent_module.build_prompt()` 读取以调整AI的回复风格。
* **`agent_feedback_memory = {...}`**
    * 为每个Agent存储一个 `deque(maxlen=5)`，用于记录用户对该Agent的最近5条元反馈（由 `agent_module.update_agent_meta_feedback()` 填充）。
* **`indexes = {}`**
    * 一个空字典，在程序启动时由 `rag_module.load_and_init_indexes()` 填充，存储所有加载的FAISS索引和语料库。
* **`session_conversations = {FIXED_SESSION_ID: []}`**
    * 存储固定会话的聊天历史记录。
* **`session_emotion_history = {FIXED_SESSION_ID: []}`**
    * 存储固定会话的情绪历史记录。

### 核心函数

* **`average_emotion()`**
    * 计算 `emotion_memory` 队列中所有情绪值的平均值。
* **`global_tone_and_temp()`**
    * 根据 `average_emotion()` 的结果，动态返回一个 (语气提示, LLM温度) 元组。如果平均情绪很低，它会返回 ("extra gentle", 0.4)，使AI回复更谨慎和温暖。

---

## 5. `emotion_module.py` - 情绪与意图分析

**文件职责**: 负责从用户输入中提取情绪和意图。

### 核心变量

* **`emotion_classifier = pipeline(...)`**
    * 加载 `j-hartmann/emotion-english-distilroberta-base` 模型，这是一个Hugging Face的Transformer模型，用于文本情绪分类。
* **`VALENCE = {...}`**
    * 一个字典，将模型输出的20多种情绪标签（如 "sadness", "joy"）映射到一个标准化的情绪效价数值（-1.0 到 +1.0）。
* **`EMOJI_VALENCE = {...}`**
    * 一个字典，定义了常见表情符号的情绪值，用于调整文本情绪。
* **`SIX_DIMENSIONS_MAP = {...}`**
    * 一个字典，将详细的情绪标签归类为六个主要维度（"happy", "sad", "angry" 等），用于 `utils.py` 中的日志统计。

### 核心函数

* **`emoji_valence_adjust(text, base_val)`**
    * 检查文本中的表情符号，并使用 `EMOJI_VALENCE` 字典来修正 `base_val`（基础情绪值）。
* **`detect_emotion(text)`**
    * **功能**: 核心情绪检测函数。
    * **流程**:
        1.  调用 `emotion_classifier` 对文本进行分类，获取置信度最高的情绪标签 (如 "sadness") 和分数 (如 0.95)。
        2.  使用 `VALENCE` 字典将情绪标签转换为原始的情绪值 (如 -0.8)。
        3.  调用 `emoji_valence_adjust()` 对情绪值进行微调。
        4.  使用 `SIX_DIMENSIONS_MAP` 找到对应的六维度标签。
        5.  返回 (情绪标签, 置信度分数, 调整后的情绪值, 六维度标签)。
* **`stable_emotion_fusion(...)`**
    * **功能**: 情绪平滑与稳定机制。
    * **逻辑**: 防止情绪在对话中剧烈跳变。如果当前检测到的情绪置信度很低（< 0.55），或者情绪类别变化过快（如从 "joy" 突然到 "anger"），它会继承或平滑上一轮的情绪值，使对话情绪更具“惯性”。
* **`detect_intent(text: str)`**
    * **功能**: 轻量级意图识别。
    * **逻辑**: 使用正则表达式（Regex）和关键词（如 "joke", "help", "why"）来快速将用户意图分类为 "fun", "help", "ask" 或 "chat"。

---

## 6. `agent_module.py` - Agent 人格与路由

**文件职责**: 定义AI的“人格”，管理Agent的选择（路由），构建最终的Prompt，并根据用户反馈（情绪或元反馈）更新Agent。

### 核心变量

* **`AGENTS = {...}`**
    * 定义了三个核心Agent人格（`empathetic`, `counselor`, `funny`）。
    * 每个人格都包含 `role` (角色), `objective` (目标), `tone` (语气) 和 `avoid` (避免做的事)。这是Prompt工程的核心。
* **`user_prefs = {...}`**
    * 定义了一组**默认**的用户偏好。注意：这个变量会被 `state.user_prefs` 的值所覆盖。

### 核心函数

* **`build_global_persona(user_prefs)`**
    * 读取 `state.user_prefs`，构建一个"[Global User Persona Settings]"文本块，告诉LLM用户偏好的全局基调（如 "Tone: formal", "Length: short"）。
* **`build_prompt(agent_name, context, ...)`**
    * **功能**: 动态构建最终发送给LLM的完整Prompt。
    * **结构**: 这是一个复杂的字符串拼接过程：
        1.  **Agent 身份**: 从 `AGENTS` 字典中获取 `role`, `objective` 等。
        2.  **反思注入**: 从 `state.agent_feedback_memory` 中读取该Agent的近期反馈（如 "I should provide more concise answers."），并注入到Prompt中，实现即时学习。
        3.  **用户偏好**: 再次注入 `user_prefs`，作为对全局人格的补充或覆盖。
        4.  **行为约束 (Guardrails)**: 添加硬编码的规则（如 "Validate pain ONLY if distress... is explicit."）。
        5.  **RAG 上下文**: 注入从 `rag_module` 检索到的 `[Retrieved Context]`。
* **`choose_agent_gen3(emo, intent, val, ...)`**
    * **功能**: 核心的Agent路由（选择）逻辑。
    * **规则**:
        1.  **硬规则**: 如果 `intent == "help"` 或情绪值极低，强制选择 `counselor`。
        2.  **硬规则**: 如果 `intent == "fun"`，强制选择 `funny`。
        3.  **软规则 (Softmax 抽样)**:
            * 获取 `state.agent_scores` 中的基础得分。
            * 根据当前情绪值（`val`）应用“情绪偏置”（`tilt`）。例如，如果情绪是正向的，`empathetic` 和 `funny` 的权重会轻微增加。
            * 使用 `numpy.random.choice` 按最终的概率分布随机选择一个Agent。
* **`update_agent_reward(agent, prev_val, adj_val, ...)`**
    * **功能**: 基于情绪变化的Agent强化学习。
    * **逻辑**: 在 `main.py` 非元模式下被调用。它比较 `prev_val` (上一轮情绪) 和 `adj_val` (当前情绪)。
    * 如果情绪改善（`adj_val > prev_val`），则增加 `agent` 在 `state.agent_scores` 中的得分（奖励）。
    * 如果情绪恶化，则降低其得分（惩罚）。
* **`update_agent_meta_feedback(agent, user_input, meta_key, meta_meaning)`**
    * **功能**: 基于元反馈的Agent反思。
    * **逻辑**: 在 `main.py` 的元模式下被调用。
    * 它会**调用LLM**（`llama-3.1-8b-instruct`），向其展示用户的反馈 (如 "you are too long")，并要求LLM生成一句反思 (如 "I should provide more concise answers.")。
    * 这句反思被存入 `state.agent_feedback_memory[agent]` 中，并在下一轮 `build_prompt` 时被注入。

---

## 7. `rag_module.py` - RAG 检索模块

**文件职责**: 负责创建、加载和查询向量索引 (FAISS)，为 "empathetic" 和 "counselor" Agent 提供外部知识。

### 核心函数

* **`embed_texts(texts, input_type="passage", ...)`**
    * **功能**: 文本嵌入功能。
    * **逻辑**: 接收一个文本列表，分批（`batch_size=32`） 调用 `config.client.embeddings.create()`。
    * **模型**: 使用 `nvidia/llama-3.2-nv-embedqa-1b-v2` 嵌入模型，将文本转换为向量。
* **`build_faiss_index(texts, name="empathy", ...)`**
    * **功能**: 构建并持久化FAISS索引。
    * **逻辑**:
        1.  **检查缓存**: 检查本地是否已存在 `faiss_{name}.index` 和 `faiss_{name}_corpus.json` 文件。如果存在，则直接用 `faiss.read_index()` 加载，跳过昂贵的嵌入步骤。
        2.  **文本分块**: 如果没有缓存，使用 `utils.chunk_text` 将长文本切片。
        3.  **嵌入**: 调用 `embed_texts` 将所有文本块转换为向量。
        4.  **构建索引**: 创建一个 `faiss.IndexFlatL2` 索引，并将向量 `add` 进去。
        5.  **保存**: 调用 `faiss.write_index()` 和 `json.dump()` 将索引和语料库保存到磁盘。
* **`load_datasets_dual()`** (在 `load_and_init_indexes` 中被调用)
    * **功能**: 从 `kagglehub` 下载预处理过的数据集（`counseling-and-empathy-top-replies`），并为 "empathy" 和 "counselor" 分别构建索引。
* **`load_and_init_indexes()`**
    * **功能**: 在 `main.py` 启动时执行的入口函数。
    * **逻辑**: 调用 `load_datasets_dual()` 来加载或构建所有必需的索引，然后使用 `indexes.update(loaded_data)` 将结果**填充到 `state.indexes` 字典中**。
* **`retrieve_context(index, corpus, query, k=3)`**
    * **功能**: 核心的检索函数。
    * **逻辑**:
        1.  调用 `embed_texts([clean_query], input_type="query")` 将用户查询（`query`）向量化。
        2.  使用 `index.search(qv, k)` 在FAISS索引中查找最相似的 `k` 个向量。
        3.  根据返回的索引 (`I`)，从 `corpus`（语料库）中提取对应的原始文本。
        4.  将这 `k` 个文本片段拼接成一个字符串返回。

---

## 8. `meta_module.py` - 元反馈处理

**文件职责**: 识别用户何时在*评论AI本身*（而不是在进行正常对话），并解释这些评论的含义。

### 核心变量

* **`META_PATTERNS = {...}`**
    * 一个字典，定义了用于快速检测的关键词（如 "shorter", "too formal"）及其含义。

### 核心函数

* **`detect_meta_feedback(text: str)`**
    * **功能**: 快速关键词检测。
    * **逻辑**: 遍历 `META_PATTERNS`，并使用正则表达式（`re.search`）查找 "you", "model", "ai" 等词。如果匹配到，立即返回关键词和含义。
* **`interpret_feedback(user_input)`**
    * **功能**: （在当前代码中未被 `main.py` 直接调用，但功能完备）使用LLM来*解释*更模糊的自然语言反馈。
    * **逻辑**:
        1.  构建一个Prompt，要求LLM分析用户输入（如 "please be warmer"）。
        2.  要求LLM在 `reply_length`, `tone`, `positivity` 等维度上返回一个JSON对象（如 `{"tone": "warmer"}`）。
        3.  这个JSON结果（如果被使用）可以被用来更新 `state.user_prefs`。

---

## 9. `utils.py` - 通用工具函数

**文件职责**: 提供被项目其他所有模块共享的、可重用的辅助函数。

### 核心函数

* **`safe_text(text: str)` 和 `safe_batch(texts)`**
    * **功能**: 文本清理。
    * **逻辑**: 使用正则表达式移除所有非 ASCII 字符和多余的空白，确保传递给模型（尤其是嵌入模型）的文本是干净的。
* **`chunk_text(text, max_chars=1000, overlap=100)`**
    * **功能**: 文本分块。
    * **逻辑**: 将长文本（`text`）切割成最大长度为 `max_chars` 的多个块，块之间有 `overlap` 字符的重叠。这是 RAG 索引构建 (`rag_module.build_faiss_index`) 的关键前置步骤。
* **`log_emotion_entry(log_data: dict)`**
    * **功能**: 写入日志。
    * **逻辑**: 接收一个字典（由 `main.py` 组装），为其添加时间戳，将其序列化为 JSON 字符串，并以追加（`'a'`）模式写入 `emotion_log.jsonl` 文件中。
* **`read_emotion_log()`**
    * **功能**: 读取日志。
    * **逻辑**: 打开 `emotion_log.jsonl` 文件，逐行读取，将每一行的 JSON 字符串解析回字典，最后返回一个包含所有日志条目的列表。供 `app.py` 的 `/api/emotion_log` 端点使用。
* **`get_daily_emotion_distribution()`**
    * **功能**: 统计当日情绪。
    * **逻辑**:
        1.  调用 `read_emotion_log()` 获取所有日志。
        2.  过滤出时间戳为“今天”的日志。
        3.  使用 `collections.Counter` 统计日志中 `emotion_dimension` 字段（来自 `emotion_module` 的六维度标签）的出现次数。
        4.  返回一个包含六个维度计数的字典。供 `app.py` 的 `/api/daily_emotion_distribution` 端点使用。