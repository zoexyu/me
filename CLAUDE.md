# 自己.skill 项目空间

## 荔枝 Token 追踪插件

**位置**: [strawberry-widget/](strawberry-widget/)
**入口**: `strawberry-widget/strawberry_widget.py`
**启动**: 双击桌面「荔枝Token」快捷方式

### 功能
桌面悬浮窗，实时追踪 Claude Code 的 token 使用量、缓存命中率。
- 迷你态 76×76（默认）→ 鼠标悬浮展开为 228×268 详细面板
- 60s 无 token 活动自动隐藏，有活动自动浮现
- 右上角置顶，无边框，可拖拽
- 系统托盘荔枝图标

### 技术栈
- Python 3.12 + tkinter（内置，零额外 GUI 依赖）
- pystray + Pillow（系统托盘）
- 数据来源：`~/.claude/projects/*/sessionId.jsonl` 的 usage 字段

### 数据指标
- `input_tokens` — 输入
- `output_tokens` — 输出
- `cache_creation_input_tokens` — 缓存写入
- `cache_read_input_tokens` — 缓存读取
- 命中率 = cache_read / total × 100%

### 关键路径
| 用途 | 路径 |
|------|------|
| 主程序 | [strawberry-widget/strawberry_widget.py](strawberry-widget/strawberry_widget.py) |
| 图标资源 | [strawberry-widget/assets/](strawberry-widget/assets/) |
| 安装脚本 | [strawberry-widget/scripts/install.bat](strawberry-widget/scripts/install.bat) |
| 设计规划 | `~/.claude/plans/idempotent-rolling-alpaca.md` |

### 踩过的坑
- **Electron**: npm 下载证书错误，放弃
- **pywebview**: Windows 无障碍服务递归 bug（AccessibilityObject 死循环），放弃
- **最终方案**: tkinter Canvas 自绘 UI，稳定可靠无外部依赖

### 2026-05-09 美化已完成
- 卡片多层阴影、指标卡片彩色竖条、缓存命中率环形图
- 历史峰值追踪、token 变化闪烁反馈、面板切换 ease-out 动画
- 迷你态 76×76 → 展开 228×268
