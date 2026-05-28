"""
MIMO Vision MCP Server - 修复版
原版 mimo-image-recognition-mcp 的认证头与 tokenplan API 不兼容
"""

import base64
import mimetypes
import os
from pathlib import Path
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mimo-vision")


def load_settings() -> dict[str, str]:
    api_key = os.getenv("MIMO_API_KEY")
    api_base = os.getenv("MIMO_API_BASE", "https://token-plan-cn.xiaomimimo.com/v1")
    model = os.getenv("MIMO_MODEL", "mimo-v2.5")

    if not api_key:
        raise RuntimeError("缺少 MIMO_API_KEY 环境变量")

    return {
        "api_key": api_key,
        "api_base": api_base.rstrip("/"),
        "model": model,
    }


def guess_mime(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    if mime and mime.startswith("image/"):
        return mime
    suffix = path.suffix.lower()
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }.get(suffix, "image/jpeg")


def to_data_url(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"图片不存在: {path}")
    mime = guess_mime(p)
    with open(p, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"


def build_image_urls(
    image_path: str | None,
    image_url: str | None,
    image_paths: list[str] | None,
    image_urls: list[str] | None,
) -> list[str]:
    urls = []
    if image_path:
        urls.append(to_data_url(image_path))
    if image_paths:
        urls.extend(to_data_url(p) for p in image_paths)
    if image_url:
        urls.append(image_url)
    if image_urls:
        urls.extend(image_urls)
    if not urls:
        raise ValueError("至少提供一张图片（image_path/image_paths/image_url/image_urls）")
    return urls


@mcp.tool()
async def understand_image(
    prompt: str,
    image_path: str | None = None,
    image_url: str | None = None,
    image_paths: list[str] | None = None,
    image_urls: list[str] | None = None,
    system_prompt: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 12000,
) -> str:
    """
    调用小米 MIMO 多模态模型理解图片。

    支持单图和多图。用于：读取、描述、比较、OCR、提取文字、分析、分类图片。

    Args:
        prompt: 图片理解任务，例如"提取图中文字""比较两张截图差异"
        image_path: 单张本地图片路径
        image_url: 单张网络图片 URL 或 data:image base64
        image_paths: 多张本地图片路径列表
        image_urls: 多张网络图片 URL 列表
        system_prompt: 可选系统提示词
        temperature: 输出随机性，越低越稳定
        max_tokens: 最大输出长度
    """
    settings = load_settings()
    image_url_values = build_image_urls(image_path, image_url, image_paths, image_urls)

    content: list[dict[str, Any]] = []
    for url in image_url_values:
        content.append({"type": "image_url", "image_url": {"url": url}})
    content.append({"type": "text", "text": prompt})

    messages: list[dict[str, Any]] = []
    if system_prompt and system_prompt.strip():
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": content})

    endpoint = f"{settings['api_base']}/chat/completions"

    # 修复：tokenplan 用 Bearer 认证，不是 api-key
    headers = {
        "Authorization": f"Bearer {settings['api_key']}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            endpoint,
            headers=headers,
            json={
                "model": settings["model"],
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )

    if response.status_code != 200:
        return f"API 请求失败 ({response.status_code}): {response.text}"

    try:
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception:
        return f"API 返回格式异常: {response.text[:500]}"


def main():
    mcp.run()


if __name__ == "__main__":
    main()
