"""DeepSeek API 对话模块"""

import os
from openai import OpenAI

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"

_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    return _client


def chat(messages: list[dict], schema_text: str) -> str:
    """发送对话请求，返回 AI 回复文本"""
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("未设置 DEEPSEEK_API_KEY 环境变量。请在终端运行: export DEEPSEEK_API_KEY='你的密钥'")

    from .prompts import build_system_prompt

    system_prompt = build_system_prompt(schema_text)
    full_messages = [
        {"role": "system", "content": system_prompt},
        *messages
    ]

    client = get_client()
    resp = client.chat.completions.create(
        model=MODEL,
        messages=full_messages,
        max_tokens=4096,
        temperature=0.3,
        stream=False,
    )

    return resp.choices[0].message.content


def chat_stream(messages: list[dict], schema_text: str):
    """流式对话，逐段 yield 文本"""
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("未设置 DEEPSEEK_API_KEY 环境变量")

    from .prompts import build_system_prompt

    system_prompt = build_system_prompt(schema_text)
    full_messages = [
        {"role": "system", "content": system_prompt},
        *messages
    ]

    client = get_client()
    stream = client.chat.completions.create(
        model=MODEL,
        messages=full_messages,
        max_tokens=4096,
        temperature=0.3,
        stream=True,
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
