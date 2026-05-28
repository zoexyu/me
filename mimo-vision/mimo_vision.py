"""
MIMO Vision - 小米 MIMO 图片识别工具
用法: python mimo_vision.py <图片路径> [提示词]
"""

import sys
import base64
import argparse
import requests
from pathlib import Path


API_BASE = "https://token-plan-cn.xiaomimimo.com/v1"
MODEL = "mimo-v2.5"


def encode_image(image_path: str) -> tuple[str, str]:
    """读取图片并转为 base64，返回 (base64数据, mime类型)"""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"图片不存在: {image_path}")

    suffix = path.suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    mime = mime_map.get(suffix, "image/jpeg")

    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    return data, mime


def recognize(image_path: str, prompt: str = "请描述这张图片的内容", api_key: str = None) -> str:
    """调用 MIMO API 识别图片"""
    if not api_key:
        raise ValueError("需要提供 API Key")

    image_data, mime = encode_image(image_path)

    response = requests.post(
        f"{API_BASE}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime};base64,{image_data}"},
                        },
                    ],
                }
            ],
        },
        timeout=60,
    )

    if response.status_code != 200:
        raise Exception(f"API 请求失败 ({response.status_code}): {response.text}")

    result = response.json()
    return result["choices"][0]["message"]["content"]


def main():
    parser = argparse.ArgumentParser(description="MIMO 图片识别")
    parser.add_argument("image", help="图片路径")
    parser.add_argument("-p", "--prompt", default="请描述这张图片的内容", help="提示词")
    parser.add_argument("-k", "--key", help="API Key（也可设环境变量 MIMO_API_KEY）")
    args = parser.parse_args()

    import os
    api_key = args.key or os.environ.get("MIMO_API_KEY")
    if not api_key:
        print("错误: 请通过 -k 参数或 MIMO_API_KEY 环境变量提供 API Key", file=sys.stderr)
        sys.exit(1)

    try:
        result = recognize(args.image, args.prompt, api_key)
        print(result)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
