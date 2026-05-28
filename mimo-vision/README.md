# MIMO Vision

用小米 MIMO 多模态模型做图片识别，支持 CLI 和 MCP 两种用法。

## 为什么做这个

Claude Code 是一个很棒的 AI 编程框架，但它默认只支持自家的 Claude 模型。如果你用其他模型（比如小米的 MIMO）跑 Claude Code，MCP 工具就废了——因为 MCP 的 tool calling 协议是 Claude 模型特有的，其他模型不认识。

但图片识别这个需求太常见了。我不想为了看一张图专门切回 Claude 模型，也不想每次都打开浏览器去 API playground 手动调。

所以我做了这个：一个干净的 Python 脚本，直接调 MIMO 的 API，绕过 MCP，哪里都能用。

## 思路

```
Claude Code + MIMO 模型
        │
        │  MCP tool calling ❌ （MIMO 不支持 tool_use 协议）
        │
        ▼
  MCP Server (server.py) ─── 能跑，但模型调不动它
        │
        │  改成直接调用 ✅
        │
        ▼
  CLI 脚本 (mimo_vision.py) ─── 终端直接跑，不依赖 MCP
        │
        │  再包一层
        │
        ▼
  Claude Code Skill ─── /mimo-ask 命令，对话中直接用
```

核心就一件事：把图片 base64 编码，POST 到 MIMO 的 OpenAI 兼容接口，拿回结果。

## 安装

```bash
pip install requests
```

仅此一个依赖。没有 GUI 框架，没有 Electron，没有 node_modules。

## 使用

### CLI

```bash
# 基本用法
python mimo_vision.py 图片.jpg

# 自定义提示词
python mimo_vision.py 图片.jpg -p "提取图中的文字"

# 指定 API Key
python mimo_vision.py 图片.jpg -k your-api-key

# 或用环境变量
export MIMO_API_KEY=your-api-key
python mimo_vision.py 图片.jpg
```

### Claude Code Skill

如果你也在用 Claude Code 跑非 Claude 模型，可以把它装成 skill：

1. 在项目的 `.claude/skills/mimo-ask/` 下创建 `skill.md`
2. 内容参考本项目的 `skill.md` 模板
3. 在对话中输入 `/mimo-ask 图片路径` 即可

### 作为 Python 模块

```python
from mimo_vision import recognize

result = recognize("图片.jpg", "描述图片内容", api_key="your-key")
print(result)
```

### MCP Server（需要模型支持 tool_use）

如果你用的是 Claude 模型，`server.py` 可以作为 MCP server 正常使用：

```bash
python server.py
```

## 获取 API Key

前往 [小米 MIMO TokenPlan](https://token-plan.xiaomimimo.com) 注册获取。

## 支持的图片格式

JPEG / PNG / GIF / WebP

## 项目结构

```
mimo-vision/
├── mimo_vision.py   # CLI 脚本 + Python 模块
├── server.py        # MCP server（供支持 tool_use 的模型使用）
└── README.md
```

## License

MIT
