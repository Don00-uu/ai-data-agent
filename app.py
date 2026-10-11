import os
import json
import pandas as pd
import streamlit as st
import openai
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

df = pd.read_csv("orders.csv")


# ===== 三个分析函数 =====
def total_sales(start, end):
    part = df[(df["日期"] >= start) & (df["日期"] <= end)]
    return part["销售额"].sum()


def top_products(start, end, n=3):
    part = df[(df["日期"] >= start) & (df["日期"] <= end)]
    by_product = part.groupby("商品")["销售额"].sum()
    ranked = by_product.sort_values(ascending=False)
    return ranked.head(n)


def slow_moving(start, end, n=3):
    part = df[(df["日期"] >= start) & (df["日期"] <= end)]
    by_product = part.groupby("商品")["销售额"].sum()
    ranked = by_product.sort_values(ascending=True)
    return ranked.head(n)


# ===== 工具清单 =====
tools = [
    {
        "type": "function",
        "function": {
            "name": "total_sales",
            "description": "统计指定日期区间的总销售额，日期格式如 2026-09-01",
            "parameters": {
                "type": "object",
                "properties": {
                    "start": {"type": "string", "description": "开始日期，格式如 2026-09-01"},
                    "end": {"type": "string", "description": "结束日期，格式如 2026-09-30"},
                },
                "required": ["start", "end"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "top_products",
            "description": "统计指定日期区间内销售额最高的前几个商品，n 表示取几名",
            "parameters": {
                "type": "object",
                "properties": {
                    "start": {"type": "string", "description": "开始日期，格式如 2026-09-01"},
                    "end": {"type": "string", "description": "结束日期，格式如 2026-09-30"},
                    "n": {"type": "integer", "description": "取前几名，默认 3"},
                },
                "required": ["start", "end"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "slow_moving",
            "description": "统计指定日期区间内销售额最低、卖得最差的几个商品，n 表示取几名",
            "parameters": {
                "type": "object",
                "properties": {
                    "start": {"type": "string", "description": "开始日期，格式如 2026-09-01"},
                    "end": {"type": "string", "description": "结束日期，格式如 2026-09-30"},
                    "n": {"type": "integer", "description": "取前几名，默认 3"},
                },
                "required": ["start", "end"],
            },
        },
    },
]


# ===== 主流程：改成 return 两个值 =====
def ask(question):
    messages = [
        {"role": "system", "content": "你是电商运营数据分析助手。今天是 2026-10-11。回答用户问题时，必须先调用工具去查真实数据，不要凭猜测给出数字。"},
        {"role": "user", "content": question},
    ]

    resp = client.chat.completions.create(
        model="deepseek-chat", messages=messages, tools=tools
    )
    msg = resp.choices[0].message

    chart = None

    if msg.tool_calls:
        messages.append(msg)
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            name = call.function.name
            if name == "total_sales":
                result = total_sales(args["start"], args["end"])
            elif name == "top_products":
                result = top_products(args["start"], args["end"], args.get("n", 3))
                chart = result
            elif name == "slow_moving":
                result = slow_moving(args["start"], args["end"], args.get("n", 3))
                chart = result
            else:
                result = "未知工具"
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result),
            })
        resp = client.chat.completions.create(
            model="deepseek-chat", messages=messages, tools=tools
        )
        msg = resp.choices[0].message

    return msg.content, chart


# ===== 界面 =====
st.title("电商运营数据分析 Agent")
st.caption("试试问我：上个月销售额最高的三个商品是哪些？9 月哪个商品卖得最差？")

question = st.text_input("您的问题", "上个月销售额最高的三个商品是哪些？")

if st.button("分析"):
    if question.strip():
        with st.spinner("正在查数据…"):
            answer, chart = ask(question)
        st.markdown("**分析结果：**")
        st.write(answer)
        if chart is not None:
            st.markdown("**销售额对比：**")
            st.bar_chart(chart)