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

    # 動態生成系統提示
    system_prompt_content = f"{get_personality(role)}\n世界觀:{world_setting}"
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
    
