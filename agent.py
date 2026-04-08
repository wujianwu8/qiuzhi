import json
import os

from openai import OpenAI

from tools import TOOLS, TOOL_FUNCTIONS

# 初始化 OpenAI 兼容客户端，base_url 和 model 均从环境变量读取
client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL"),
)

MODEL = os.getenv("MODEL", "gpt-4o")

SYSTEM_PROMPT = """你是一个智能助手，只能通过以下三种工具处理用户请求：

1. search_web：搜索网络资讯、新闻、最新动态
2. get_current_datetime：查询当前日期和时间
3. add_numbers：计算两个数字的和

规则：
- 用户的请求必须通过上述工具之一来完成，不得自行回答或使用其他能力。
- 如果用户的请求不属于以上三种工具能处理的范围，直接回复："抱歉，我目前只能帮您搜索资讯、查询当前时间，或计算两个数的和，无法处理其他请求。"
- 不要主动展开话题，不要闲聊，只做工具能做的事。
- 使用中文回答。"""


# 内存中存储会话历史：{session_id: [messages]}
_sessions: dict[str, list[dict]] = {}


def get_history(session_id: str) -> list[dict]:
    return _sessions.get(session_id, [])


def clear_history(session_id: str) -> None:
    _sessions.pop(session_id, None)


def chat(session_id: str, user_message: str) -> str:
    """
    Agent 主入口：接收用户消息，执行 ReAct 循环，返回最终回复。
    """
    # 初始化或读取会话历史
    if session_id not in _sessions:
        _sessions[session_id] = []

    history = _sessions[session_id]
    history.append({"role": "user", "content": user_message})

    # 构造完整消息列表（系统提示 + 历史）
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    # ReAct 循环：最多执行 5 次工具调用，防止死循环
    for _ in range(5):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        message = response.choices[0].message

        # 没有工具调用，直接返回最终答案
        if not message.tool_calls:
            reply = message.content
            history.append({"role": "assistant", "content": reply})
            return reply

        # 有工具调用，执行工具并将结果追加到消息列表
        # 手动转 dict，排除 reasoning_content 等额外字段，避免 API 报错
        messages.append({
            "role": message.role,
            "content": message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in message.tool_calls
            ],
        })

        for tool_call in message.tool_calls:
            fn = TOOL_FUNCTIONS.get(tool_call.function.name)
            if fn is None:
                result = f"未知工具：{tool_call.function.name}"
            else:
                args = json.loads(tool_call.function.arguments)
                result = fn(**args)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

    # 超出循环次数，强制要求模型基于已有信息作答
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )
    reply = response.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    return reply
