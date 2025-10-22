# app.py
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import json
import uvicorn
from main import chat_fn     
import utils
import state

app = FastAPI(title="EmoAI API")

# 流式输出接口
# app.py

# ... (你的 import 保持不变) ...

# 流式输出接口
@app.post("/api/chat/stream")
async def chat_stream(request: Request):
    data = await request.json()
    user_input = data.get("user_input", "")
    tone = data.get("tone", data.get("tone_level", 0.6))
    
    # --- 1. 在函数*顶部*读取所有可选参数 ---
    agent_override = data.get("agent_override", None)
    
    # --- 2. 直接获取固定会话的历史记录 ---
    try:
        chat_history_session = state.session_conversations[state.FIXED_SESSION_ID]
        emotion_history_session = state.session_emotion_history[state.FIXED_SESSION_ID]
    except KeyError:
        # 预防万一, 如果 state.py 没初始化成功, 就在这里初始化
        state.session_conversations[state.FIXED_SESSION_ID] = []
        state.session_emotion_history[state.FIXED_SESSION_ID] = []
        chat_history_session = state.session_conversations[state.FIXED_SESSION_ID]
        emotion_history_session = state.session_emotion_history[state.FIXED_SESSION_ID]
    
    # --- 3. 在这里安全地获取两个列表 ---
    #chat_history_session = state.session_conversations[session_id]
    #emotion_history_session = state.session_emotion_history[session_id]

    async def event_stream():
        try:
            # *** (关键修复) ***
            # main.py (chat_fn) 现在直接 yield 字典。
            # 我们不再需要检查4元组，直接将字典传递给客户端。
            
            for output_dict in chat_fn(
                user_input,
                chat_history=chat_history_session,
                tone=tone,
                agent_override=agent_override,
                emotion_history=emotion_history_session
            ):
                
                # 检查是否是一个有效的字典 (以防万一)
                if isinstance(output_dict, dict):
                    # 直接将 main.py 提供的字典序列化并发送
                    yield f"data: {json.dumps(output_dict)}\n\n"
                    
                    # 如果 main.py 说这是最后一块，我们就停止
                    if output_dict.get("is_final", False):
                        break
                else:
                    # 备用逻辑，万一 main.py 格式又错了
                    print(f"⚠️ chat_fn 返回了意外格式 (应为 dict): {output_dict}")


        except Exception as e:
                # 打印更详细的错误信息
                import traceback
                print(f"[FastAPI Error in event_stream] {e}")
                traceback.print_exc() # 打印完整 traceback 到服务器控制台
                error_output = {
                    "error": str(e), # 把错误信息发给客户端
                    "report": "An error occurred on the server.",
                    "is_final": True
                }
                yield f"data: {json.dumps(error_output)}\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")
# 日志接口
@app.get("/api/emotion_log")
async def get_emotion_log():
    """
    获取所有已保存的情绪日志条目。
    """
    log_data = utils.read_emotion_log()
    
    # 按时间倒序返回 (最新的在最前面)，方便前端显示
    return sorted(log_data, key=lambda x: x.get("timestamp", ""), reverse=True)

#当日情绪分布接口
@app.get("/api/daily_emotion_distribution")
async def get_daily_distribution():
    distribution_data = utils.get_daily_emotion_distribution()
    return distribution_data

# 启动服务器的指令 (保持不变)
if __name__ == "__main__":
    print("启动 FastAPI 服务器")
    print("访问 http://127.0.0.1:8000/docs 查看 API 文档")
    # 注意：在 main.py 加载 RAG 索引可能需要几秒钟
    # 确保在 uvicorn.run 之前，main.py 中的 rag_module.load_and_init_indexes() 已经执行完毕
    # (因为 app.py 导入了 main.py, main.py 顶层的代码会先执行, 所以这是OK的)
    uvicorn.run(app, host="0.0.0.0", port=8000)