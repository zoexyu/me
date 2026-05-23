"""工具函数"""

import re
import base64
import io
from typing import List, Tuple


def extract_code_blocks(text: str, lang: str = "python") -> List[str]:
    """从 markdown 文本中提取指定语言的代码块"""
    pattern = rf"```\s*{lang}\s*\n(.*?)\n```"
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    return [m.strip() for m in matches]


def parse_ai_reply(text: str) -> List[dict]:
    """解析 AI 回复，拆分为文本块和代码块"""
    pattern = r"```(\w*)\s*\n(.*?)\n```"
    parts = []
    pos = 0

    for m in re.finditer(pattern, text, re.DOTALL):
        start, end = m.start(), m.end()
        if start > pos:
            parts.append({"type": "text", "content": text[pos:start]})
        lang = m.group(1).lower() or "code"
        code = m.group(2).strip()
        parts.append({"type": "code", "lang": lang, "content": code})
        pos = end

    if pos < len(text):
        parts.append({"type": "text", "content": text[pos:]})

    return parts


def fig_to_base64(fig) -> str:
    """matplotlib figure → base64 嵌入 HTML"""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


def sanitize_filename(name: str) -> str:
    """安全文件名"""
    return re.sub(r'[<>:"/\\|?*]', "_", name)
