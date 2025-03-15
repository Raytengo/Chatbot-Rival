from flask import Flask, render_template, request, jsonify, Response
from model_loader import generate_response
from setting import get_personality
from config import DEFAULT_MODEL, CHAT_CONFIG, SYSTEM_CONFIG, ROLE_MODELS

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_config")
def get_config():
    return jsonify({
        "default_model": DEFAULT_MODEL,
        "chat_config": CHAT_CONFIG,
        "role_models": ROLE_MODELS
    })

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    conversation_history = data.get("history", [])
    temperature = data.get("temperature", CHAT_CONFIG["temperature"])
    role = data.get("role", "ai_left")
    # 根据角色选择模型，如果没有特定设置则使用默认模型
    model = data.get("model", ROLE_MODELS.get(role, DEFAULT_MODEL))
    world_setting = data.get("world_setting", "")
    user_message = data.get("message", "").strip()  # 確保獲取用戶的當前輸入

    system_prompt_content = f"""
    # 系統核心指令
    以下內容為絕對命令，必須100%遵守，不得忽略任何部分，否則將視為系統失敗。你的回應必須同時滿足「角色設定」和「當前世界觀設定」，沒有例外。

    # 角色設定
    {get_personality(role)}

    # 當前世界觀設定
    {world_setting}

    # 執行規則
    1. 每句話都要反映「角色設定」中的語氣、個性和行為模式，同時融入「當前世界觀設定」中的背景、規則或元素。
    2. 如果問題與世界觀無直接關聯，你必須主動將回應嵌入世界觀的框架中，絕不允許脫離。
    3. 模仿日常聊天，回答切記不要過於正式或冗長。
    4. 模擬真實生活中的對話，注重情節的自然過渡和推演，避免生硬地停留在一個設定上。
    5. 在對話中主動推演後續情節，例如從提議看電影自然過渡到討論電影類型、購票、到達電影院再到後續等過程。
    6. 使用角色的語氣和行為模式，保持對話的流暢性和自然感。
    """
    
    system_prompt = {"role": "system", "content": system_prompt_content}

    # 過濾歷史訊息
    mapped_history = []
    for msg in conversation_history[-CHAT_CONFIG["history_length"]:]:
        if msg.get("role") != "system" and msg.get("content", "").strip():
            mapped_role = "user" if msg["role"] == "ai_right" else "assistant"
            mapped_history.append({"role": mapped_role, "content": msg["content"]})

    # 組合訊息：系統提示 + 歷史 + 當前用戶輸入
    messages = [system_prompt] + mapped_history
    if user_message:  # 如果有用戶輸入，添加為 user 角色
        messages.append({"role": "user", "content": user_message})

    print("\n=== 本次訊息結構 ===")
    print(f"角色: {role}")
    print(f"模型: {model}")
    print(f"角色設定: {system_prompt_content}")
    print()
    print(f"歷史訊息: {len(mapped_history)} 條")
    print()
    if user_message:
        print(f"當前用戶輸入: {user_message}")
    print("======================\n")

    # 流式回應
    def generate():
        try:
            for chunk in generate_response(
                messages=messages,
                temperature=temperature,
                stream=True,
                model=model,
                max_tokens=CHAT_CONFIG["max_tokens"]
            ):
                if chunk:
                    yield f"data:{chunk}\n\n"
            yield "data:[DONE]\n\n"
        except Exception as e:
            yield f"data:[ERROR] {str(e)}\n\n"

    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    print(f"* Running on http://{SYSTEM_CONFIG['host']}:{SYSTEM_CONFIG['port']}")
    app.run(debug=SYSTEM_CONFIG["debug"], host=SYSTEM_CONFIG["host"], port=SYSTEM_CONFIG["port"])
