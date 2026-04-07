import os
from datetime import datetime


from tavily import TavilyClient


def search_web(query: str, max_results: int = 5) -> str:
    """使用 Tavily 搜索网络资讯，返回格式化的搜索结果文本。"""
    try:
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        response = client.search(query, max_results=max_results)
        results = response.get("results", [])

        if not results:
            return "未找到相关资讯。"

        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(f"[{i}] {r['title']}\n{r['url']}\n{r['content']}")

        return "\n\n".join(formatted)

    except Exception as e:
        return f"搜索失败：{e}"


def get_current_datetime() -> str:
    """返回当前日期和时间。"""
    now = datetime.now()
    return now.strftime("当前日期：%Y年%m月%d日，当前时间：%H:%M:%S")


def add_numbers(a: float, b: float) -> str:
    """计算两个数的和。"""
    result = a + b
    return f"{a} + {b} = {result}"


# 注册给 Agent 使用的工具定义（OpenAI function calling 格式）
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "当需要查询实时资讯、新闻、最新动态时，调用此工具在网络上搜索相关内容。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词，尽量简洁精准",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "获取当前的日期和时间。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "计算两个数字的和。",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "第一个数"},
                    "b": {"type": "number", "description": "第二个数"},
                },
                "required": ["a", "b"],
            },
        },
    },
]

# 工具名称到函数的映射
TOOL_FUNCTIONS = {
    "search_web": search_web,
    "get_current_datetime": lambda **_: get_current_datetime(),
    "add_numbers": add_numbers,
}
