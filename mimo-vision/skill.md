# MIMO Ask - 图片识别

调用小米 MIMO 模型识别/分析图片。

## 用法

用户输入 `/mimo-ask` 后会附带图片路径和可选的提示词。

## 执行步骤

1. 解析用户输入，提取图片路径（必填）和提示词（可选，默认"请描述这张图片的内容"）
2. 运行以下命令：

```bash
PYTHONIOENCODING=utf-8 MIMO_API_KEY="<你的API Key>" python "mimo-vision/mimo_vision.py" "<图片路径>" -p "<提示词>"
```

3. 将脚本输出直接展示给用户

## 安装方式

将此文件放到项目的 `.claude/skills/mimo-ask/skill.md`，并在命令中填入你的 API Key 和正确的脚本路径。

## 注意

- 图片路径可以是绝对路径或相对路径
- 支持 jpg、png、gif、webp 格式
- 如果用户只发了图片没说话，就用默认提示词描述图片内容
- 不要额外加分析，直接把 MIMO 的回复给用户看
