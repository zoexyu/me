# 药学数据分析平台 (PharmAnalyzer)

> AI 驱动的药学统计分析助手 —— 上传数据 → 用自然语言提问 → AI 推荐方法 → 一键出图

[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?logo=streamlit)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python)](https://python.org)
[![DeepSeek](https://img.shields.io/badge/AI-DeepSeek-4F6EF7)](https://deepseek.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 这是什么

专为**药学专业学生**设计的 AI 数据分析平台。你只需要：
1. 上传 CSV 数据文件
2. 用自然语言描述分析需求（如"癌种和研究阶段有没有关联？"）
3. AI 自动推荐合适的统计方法、解释原因、生成完整代码
4. 一键执行代码，即时查看结果图表

## 设计原则

| 原则 | 说明 |
|------|------|
| **方便** | 上传 CSV → 说话 → 出图，三步到头 |
| **严谨** | 统计方法经得起验收，代码直接可运行 |
| **透明** | AI 解释"为什么推荐这个方法"，学生能拿去答辩 |
| **敢拒绝** | 数据不支持时明确说不，给出替代方案 |
| **可复现** | 低温度参数，代码保留可重跑 |
| **引用来源** | 统计方法关联教材/文献，建立学术信任 |
| **少幻觉** | 宁可不答，不乱推荐 |

## 技术架构

```
浏览器 → Streamlit Cloud → Python/Streamlit
                              ├── DeepSeek API（AI 对话）
                              ├── pandas + scipy（统计分析）
                              └── matplotlib + plotly（可视化）
```

- **前端**: Streamlit（Python Web 框架）
- **AI 引擎**: DeepSeek Chat API
- **数据分析**: pandas, scipy, statsmodels
- **可视化**: matplotlib, plotly
- **部署**: Streamlit Cloud（免费）

## 本地运行

```bash
# 1. 克隆仓库
git clone https://github.com/你的用户名/pharmacy-platform.git
cd pharmacy-platform

# 2. 安装依赖
pip install -r requirements.txt

# 3. 设置 API 密钥
# Windows PowerShell:
$env:DEEPSEEK_API_KEY="你的DeepSeek密钥"
# Mac/Linux:
export DEEPSEEK_API_KEY="你的DeepSeek密钥"

# 4. 启动
streamlit run app.py
```

浏览器自动打开 `http://localhost:8501`。

## 项目结构

```
pharmacy-platform/
├── app.py                  # Streamlit 主应用
├── src/
│   ├── ai.py               # DeepSeek API 调用
│   ├── prompts.py          # 系统提示词（含 7 大原则）
│   ├── analysis.py         # 代码安全执行引擎
│   └── utils.py            # 工具函数
├── .streamlit/
│   └── config.toml         # Streamlit 配置
├── requirements.txt        # Python 依赖
└── README.md
```

## 支持的统计方法

- 分类变量关联性 → 卡方检验 / Fisher 精确检验
- 数值变量组间比较（2组）→ t 检验 / Mann-Whitney U
- 数值变量组间比较（多组）→ ANOVA / Kruskal-Wallis
- 相关性分析 → Pearson / Spearman
- 预测模型 → 逻辑回归 / 线性回归
- 趋势检验 → Cochran-Armitage / Mann-Kendall

## License

MIT © 2025 张潇予
