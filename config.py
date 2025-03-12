# 默认模型设置
DEFAULT_MODEL = "grok-2-latest"

# 可用模型列表
AVAILABLE_MODELS = [
    "deepseek-chat",
    "deepseek-reasoner",
    "grok-2-latest"
]

# 对话角色模型设置
ROLE_MODELS = {
    "ai_left": "grok-2-latest",   # 左边角色使用的模型
    "ai_right": "grok-2-latest"   # 右边角色使用的模型
}

# 对话设置
CHAT_CONFIG = {
    "history_length": 50,     # 历史记录保留的最大条数
    "temperature": 1.3,       # 生成温度
    "default_rounds": 2,      # 默认对话轮数
    "max_tokens": 2000        # 最大生成token数
}

# 系统设置
SYSTEM_CONFIG = {
    "debug": True,            # 是否开启调试模式
    "port": 5000,             # 服务器端口
    "host": "127.0.0.1"       # 服务器主机
} 