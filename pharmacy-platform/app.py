"""
药学数据分析平台 — AI 驱动的统计助手
启动：streamlit run app.py
"""

import streamlit as st
import pandas as pd
import time
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.ai import chat_stream
from src.prompts import build_schema_text
from src.utils import parse_ai_reply, fig_to_base64
from src.analysis import run_code

# ── 页面配置 ─────────────────────────────────────────
st.set_page_config(
    page_title="药学数据分析平台",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 样式 ────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background: #f7f8fc; }
[data-testid="stSidebar"] { background: #fff; border-right: 1px solid #e5e7eb; }
.code-block {
    position: relative; margin: 10px 0; border-radius: 8px;
    overflow: hidden; border: 1px solid #e5e7eb;
}
.code-header {
    display: flex; justify-content: space-between; align-items: center;
    background: #1e1e2e; padding: 6px 12px;
}
.code-lang { color: #a0a0b0; font-size: 12px; font-weight: 600; }
.code-block pre {
    margin: 0; padding: 14px 16px; background: #1a1a2e; color: #e0e0f0;
    font-size: 13px; line-height: 1.6; overflow-x: auto; white-space: pre-wrap;
}
.result-box {
    background: #f0fdf4; border: 1px solid #bbf7d0;
    border-radius: 8px; padding: 12px; margin: 8px 0;
}
.error-box {
    background: #fef2f2; border: 1px solid #fecaca;
    border-radius: 8px; padding: 12px; margin: 8px 0;
    color: #991b1b; font-size: 13px;
}
.empty-state {
    text-align: center; padding: 80px 20px; color: #9ca3af;
}
.empty-state h2 { color: #374151; font-size: 22px; margin-bottom: 8px; }
@media (max-width: 768px) {
    [data-testid="stSidebar"] { display: none; }
}
</style>
""", unsafe_allow_html=True)

# ── 会话状态初始化 ───────────────────────────────────
defaults = {
    "df": None,
    "schema_text": "",
    "messages": [],
    "results": {},
    "exec_counter": 0,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── 侧边栏 ──────────────────────────────────────────
with st.sidebar:
    st.markdown("## 数据上传")
    uploaded = st.file_uploader(
        "上传 CSV 文件", type=["csv"],
        help="支持 UTF-8 和 GBK 编码的中文 CSV",
    )

    if uploaded:
        try:
            df = pd.read_csv(uploaded)
        except UnicodeDecodeError:
            uploaded.seek(0)
            df = pd.read_csv(uploaded, encoding="gbk")

        st.session_state.df = df
        st.session_state.schema_text = build_schema_text(df)
        st.session_state.messages = []
        st.session_state.results = {}

        st.markdown("---")
        st.markdown("### 数据概览")
        st.caption(f"**行数**: {len(df):,} &nbsp;|&nbsp; **列数**: {len(df.columns)}")

        with st.expander("列详情", expanded=False):
            for col_name in df.columns:
                col = df[col_name]
                st.caption(
                    f"**{col_name}** ({col.dtype}) "
                    f"— {col.nunique()} 唯一值, {col.isna().sum()} 缺失"
                )

        with st.expander("前 20 行预览", expanded=False):
            st.dataframe(df.head(20), use_container_width=True)
    else:
        st.session_state.df = None
        st.session_state.schema_text = ""
        st.markdown("---")
        st.info("请上传 CSV 文件开始分析")

# ── 主区域 ──────────────────────────────────────────
st.title("药学数据分析平台")
st.caption("上传数据 → 用自然语言提问 → AI 推荐方法 → 执行代码 → 查看结果")

# ── 处理代码执行请求 ────────────────────────────────
if "pending" in st.session_state and st.session_state.pending:
    code = st.session_state.pending["code"]
    msg_id = st.session_state.pending["msg_id"]

    # 检查是否有已缓存的执行结果
    result_key = f"{msg_id}_{hash(code) % 100000}"
    if result_key not in st.session_state.results:
        with st.spinner("执行中..."):
            result = run_code(code, st.session_state.df)
            st.session_state.results[result_key] = result

    st.session_state.pending = None

# ── 渲染聊天消息 ─────────────────────────────────────
if st.session_state.df is None:
    st.markdown("""
    <div class="empty-state">
        <h2>开始分析</h2>
        <p>在左侧上传 CSV 数据文件，然后输入你想分析的问题</p>
        <p style="font-size:13px;margin-top:20px;">你可以这样问：</p>
        <p style="font-size:13px;">"癌种和研究阶段之间有没有关联？"</p>
        <p style="font-size:13px;">"不同年龄组的疗效差异显著吗？"</p>
        <p style="font-size:13px;">"哪些因素与药物不良反应率相关？"</p>
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    role = msg["role"]
    msg_id = msg.get("id", "")

    with st.chat_message(role):
        if role == "user":
            st.markdown(msg["content"])
            continue

        # AI 消息：解析 markdown + 代码块
        content = msg.get("content", "")
        if isinstance(content, list):
            # 已经是 parts 格式
            parts = content
        else:
            parts = parse_ai_reply(content)

        for i, part in enumerate(parts):
            if part["type"] == "text":
                st.markdown(part["content"])
            else:
                lang = part.get("lang", "code")
                code = part["content"]

                # 渲染代码块
                st.code(code, language=lang if lang in ("python", "r") else None)

                # 执行 / 复制按钮
                c1, c2, c3 = st.columns([1, 1, 10])
                code_idx = f"{msg_id}_{i}"

                # 执行按钮（仅 Python）
                if lang == "python":
                    with c1:
                        if st.button("执行", key=f"run_{code_idx}", type="primary"):
                            result = run_code(code, st.session_state.df)
                            result_key = f"{msg_id}_{hash(code) % 100000}"
                            st.session_state.results[result_key] = result
                            st.rerun()

                # 显示执行结果
                result_key = f"{msg_id}_{hash(code) % 100000}"
                if result_key in st.session_state.results:
                    result = st.session_state.results[result_key]
                    if result["success"]:
                        for tbl in result.get("tables", []):
                            if hasattr(tbl["data"], "to_dict"):
                                st.dataframe(tbl["data"], use_container_width=True)
                        for fig in result.get("plots", []):
                            try:
                                b64 = fig_to_base64(fig)
                                st.markdown(
                                    f'<img src="data:image/png;base64,{b64}" '
                                    f'style="max-width:100%;border-radius:8px;margin:8px 0;">',
                                    unsafe_allow_html=True,
                                )
                            except Exception:
                                pass
                        if result["stdout"]:
                            with st.expander("控制台输出"):
                                st.text(result["stdout"])
                    else:
                        st.markdown(
                            f'<div class="error-box"><b>执行出错</b>'
                            f'<pre>{result["error"]}</pre></div>',
                            unsafe_allow_html=True,
                        )

# ── 输入框 ──────────────────────────────────────────
prompt = st.chat_input(
    "输入你想分析的问题……",
    disabled=st.session_state.df is None,
)

if prompt:
    # 添加用户消息
    user_id = f"user_{len(st.session_state.messages)}"
    st.session_state.messages.append({
        "id": user_id, "role": "user", "content": prompt,
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # 调 AI，流式显示
    with st.chat_message("assistant"):
        api_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[:-1]
        ]

        full_reply = ""
        placeholder = st.empty()

        try:
            for chunk in chat_stream(api_messages, st.session_state.schema_text):
                full_reply += chunk
                placeholder.markdown(full_reply + "▌")

            placeholder.markdown(full_reply)

        except Exception as e:
            err = str(e)
            if "401" in err or "403" in err or "auth" in err.lower():
                err = "API 密钥无效。请设置 DEEPSEEK_API_KEY 环境变量"
            elif "429" in err:
                err = "请求太频繁，请稍等几秒再试"
            elif "timeout" in err.lower() or "timed" in err.lower():
                err = "AI 响应超时，请重试"
            placeholder.error(f"调用失败：{err}")
            full_reply = ""

        if full_reply:
            ai_id = f"ai_{len(st.session_state.messages)}"
            st.session_state.messages.append({
                "id": ai_id, "role": "assistant", "content": full_reply,
            })
            st.rerun()
