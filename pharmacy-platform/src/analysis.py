"""代码安全执行引擎"""

import sys
import io
import traceback
import warnings
from typing import Any


# 允许 import 的白名单模块
ALLOWED_IMPORTS = {
    "pandas", "numpy", "scipy", "scipy.stats", "scipy.optimize",
    "statsmodels", "statsmodels.api", "statsmodels.formula.api",
    "matplotlib", "matplotlib.pyplot",
    "seaborn", "plotly", "plotly.express", "plotly.graph_objects",
    "sklearn", "sklearn.linear_model", "sklearn.preprocessing",
    "math", "statistics", "collections", "itertools",
    "warnings", "typing",
}

BLOCKED_MODULES = {
    "os", "subprocess", "sys", "shutil", "socket", "http",
    "urllib", "requests", "ftplib", "telnetlib", "smtplib",
    "pathlib", "io", "pickle", "multiprocessing", "threading",
    "ctypes", "signal", "builtins",
}


def run_code(code: str, df) -> dict:
    """在受限环境中执行分析代码，返回结果字典"""
    # 构建受限的全局命名空间
    safe_globals = {
        "__builtins__": _safe_builtins(),
        "df": df.copy(),
    }

    # 执行环境
    local_vars = {}

    # 捕获输出
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = stdout_capture
    sys.stderr = stderr_capture

    plots = []
    tables = []
    has_error = False
    error_msg = ""

    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")

        try:
            # 预注入常用模块
            code = _inject_imports(code)

            exec(code, safe_globals, local_vars)
        except Exception as e:
            has_error = True
            error_msg = f"{type(e).__name__}: {e}\n\n{traceback.format_exc()}"
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    stdout_text = stdout_capture.getvalue()
    stderr_text = stderr_capture.getvalue()

    # 收集警告
    for w in caught_warnings:
        stderr_text += f"\n[警告] {w.category.__name__}: {w.message}"

    # 收集 matplotlib figures
    try:
        import matplotlib.pyplot as plt
        figs = [plt.figure(n) for n in plt.get_fignums()]
        for fig in figs:
            if fig.get_axes():
                plots.append(fig)
        plt.close("all")
    except Exception:
        pass

    # 收集局部变量中的 DataFrame
    for name, val in local_vars.items():
        if hasattr(val, "to_dict") and not name.startswith("_"):
            tables.append({"name": name, "data": val})

    # 检查最后一个表达式是否是 DataFrame
    if not has_error and local_vars:
        last_val = list(local_vars.values())[-1] if local_vars else None
        if hasattr(last_val, "to_dict") and not any(
            last_val is t["data"] for t in tables
        ):
            tables.append({"name": "result", "data": last_val})

    return {
        "success": not has_error,
        "error": error_msg,
        "stdout": stdout_text.strip(),
        "stderr": stderr_text.strip(),
        "plots": plots,
        "tables": tables,
    }


def _safe_builtins() -> dict:
    """返回安全的 builtins 子集"""
    safe = {}
    allowed = [
        "abs", "all", "any", "bool", "complex", "dict", "divmod",
        "enumerate", "filter", "float", "format", "frozenset",
        "int", "isinstance", "issubclass", "iter", "len", "list",
        "map", "max", "min", "next", "object", "pow", "print",
        "range", "reversed", "round", "set", "slice", "sorted",
        "str", "sum", "tuple", "type", "zip",
        "True", "False", "None", "Exception", "ValueError",
        "TypeError", "KeyError", "IndexError", "StopIteration",
        "__import__", "hasattr", "getattr", "setattr",
        "super", "property", "classmethod", "staticmethod",
        "repr", "bytes", "bytearray", "memoryview",
    ]
    for name in allowed:
        if hasattr(__builtins__, name):
            safe[name] = getattr(__builtins__, name)
        elif name in __builtins__:
            safe[name] = __builtins__[name]

    # 安全版 __import__
    def safe_import(name, *args, **kwargs):
        if name in BLOCKED_MODULES:
            raise ImportError(f"不允许导入模块: {name}")
        # 检查二级模块
        top = name.split(".")[0]
        if top in BLOCKED_MODULES:
            raise ImportError(f"不允许导入模块: {name}")
        return __import__(name, *args, **kwargs)

    safe["__import__"] = safe_import
    return safe


def _inject_imports(code: str) -> str:
    """自动注入常用 import 语句"""
    prefix = """import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go

"""
    return prefix + code
