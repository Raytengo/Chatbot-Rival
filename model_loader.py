import os
import logging
from typing import List, Dict, Optional, Union, Generator
from openai import OpenAI, APIConnectionError, APIError
from dotenv import load_dotenv
from config import CHAT_CONFIG

# 加載 .env 文件
load_dotenv()

logging.basicConfig(level=logging.WARNING)  # 設置根日誌的級別為 WARNING，這樣 INFO 類的訊息會被過濾掉

# 禁用 Werkzeug 和 Flask 的 INFO 日誌
logging.getLogger("werkzeug").setLevel(logging.WARNING)  # 禁用 Werkzeug 的 INFO 類型日誌
logging.getLogger("flask.app").setLevel(logging.WARNING)  # 禁用 Flask 應用的 INFO 類型日誌

# 設置日誌
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class DeepSeekAPIError(Exception):
    """自訂 API 錯誤異常類"""
    pass

MODEL_CONFIGS = {
    "deepseek-chat": {
        "api_key_env": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com",
        "default_max_tokens": CHAT_CONFIG["max_tokens"],
        "default_timeout": 30
    },
    "grok-2-latest": {
        "api_key_env": "GROK_API_KEY",
        "base_url": "https://api.x.ai/v1",
        "default_max_tokens": CHAT_CONFIG["max_tokens"],
        "default_timeout": 30
    }
}

def get_client(model: str) -> OpenAI:
    """
    初始化對應模型的客戶端
    :param model: 使用的模型名稱（例如 'deepseek-chat' 或 'grok-2-latest'）
    :return: 對應模型的客戶端實例
    :raises DeepSeekAPIError: 如果模型不受支援或 API 密鑰未設置
    """
    if model not in MODEL_CONFIGS:
        logger.error(f"不支持的模型: {model}")
        raise DeepSeekAPIError(f"不支持的模型: {model}")

    config = MODEL_CONFIGS[model]
    api_key = os.getenv(config["api_key_env"])

    if not api_key:
        logger.error(f"{model} API 密鑰未設置 (環境變數: {config['api_key_env']})")
        raise DeepSeekAPIError(f"{model} API 密鑰未設置 (環境變數: {config['api_key_env']})")

    return OpenAI(
        api_key=api_key,
        base_url=config["base_url"],
        timeout=config["default_timeout"]
    )

def generate_response(
    messages: List[Dict[str, str]],
    temperature: float = CHAT_CONFIG["temperature"],
    stream: bool = True,
    model: str = "deepseek-chat",
    max_tokens: Optional[int] = None
) -> Union[Generator[str, None, None], str]:
    """
    生成對話回應
    :param messages: 對話訊息列表，每個訊息為 {'role': 'user/assistant', 'content': '訊息內容'}
    :param temperature: 生成溫度，範圍 0-2
    :param stream: 是否流式返回
    :param model: 使用的模型
    :param max_tokens: 最大生成 token 數
    :yields: 如果 stream=True，逐塊返回內容
    :returns: 如果 stream=False，返回完整回應
    :raises DeepSeekAPIError: 如果 API 請求失敗
    :raises ValueError: 如果參數無效
    """
    if not 0 <= temperature <= 2:
        raise ValueError("溫度必須在 0 到 2 之間")
    if max_tokens is not None and max_tokens <= 0:
        raise ValueError("max_tokens 必須為正數")

    client = get_client(model)
    config = MODEL_CONFIGS[model]
    max_tokens = max_tokens or config["default_max_tokens"]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=stream,
            max_tokens=max_tokens
        )

        if stream:
            yield from (chunk.choices[0].delta.content or "" for chunk in response if chunk.choices[0].delta.content)
        else:
            return response.choices[0].message.content

    except APIConnectionError as e:
        error_msg = f"連接失敗: {str(e.__cause__)}"
        logger.error(error_msg)
        raise DeepSeekAPIError(error_msg) from e
    except APIError as e:
        error_msg = f"API 錯誤 (狀態碼: {e.status_code}): {e.message}"
        logger.error(error_msg)
        raise DeepSeekAPIError(error_msg) from e
    except Exception as e:
        error_msg = f"未知錯誤: {str(e)}"
        logger.error(error_msg)
        raise DeepSeekAPIError(error_msg) from e