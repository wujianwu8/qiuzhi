# QAgent

一个基于 **ReAct 架构**的 AI Agent 服务。用户可通过聊天 API 与 Agent 交互，Agent 会根据用户意图自主选择合适的工具处理请求，目前支持三种能力：

- **网络资讯搜索**：搜索并整理实时新闻、最新动态
- **查询当前时间**：返回服务器当前日期与时间
- **数字加法计算**：计算两个数字的和

对于超出上述三种能力范围的请求，Agent 会明确告知用户无法处理。

---

## 运行环境要求

| 项目 | 最低要求 |
|------|----------|
| 操作系统 | Windows 10 / macOS 12 / Ubuntu 20.04 |
| Python | **3.10 及以上** |
| 内存 | 512 MB |
| 网络 | 需能访问所配置的 LLM API 及 Tavily 搜索 API |

---

## 技术栈

- **Python 3.10+** + **FastAPI**
- **任意 OpenAI 兼容 LLM**（通过 `BASE_URL` + `MODEL` 配置，默认示例为阿里百炼 Qwen3.5-plus）
- **Tavily Search API**（网络搜索）

## Agent 核心组件

| 组件 | 实现方式 |
|------|----------|
| Planning | 系统提示定义能力边界，引导模型决策 |
| Tool Use | OpenAI function calling 格式，支持多工具注册 |
| Memory | 内存字典按 session_id 存储会话历史，支持多轮对话 |
| Action | ReAct 循环执行工具调用并将结果反馈给模型 |

## 项目结构

```
├── main.py          # FastAPI 入口，定义 API 路由
├── agent.py         # Agent 核心逻辑（ReAct 循环）
├── tools.py         # 工具定义：搜索、时间、加法
├── requirements.txt
├── .env             # 环境变量（不提交到 Git）
└── .env.example     # 环境变量示例
```

---

## 环境配置与运行

### 第一步：安装 Python

前往 [https://www.python.org/downloads/](https://www.python.org/downloads/) 下载 Python 3.10 或更高版本。

安装时勾选 **"Add Python to PATH"**，安装完成后验证：

```bash
python --version
# 输出示例：Python 3.12.0
```

### 第二步：克隆项目

```bash
git clone https://github.com/wujianwu8/qiuzhi.git
cd qiuzhi
```

### 第三步：安装依赖

```bash
pip install -r requirements.txt
```

### 第四步：配置环境变量

复制示例文件并填入 API Key：

```bash
cp .env.example .env
```

编辑 `.env`：

```
API_KEY=你的 LLM API Key
BASE_URL=https://api.openai.com/v1
MODEL=gpt-4o
TAVILY_API_KEY=你的Tavily API Key
```

支持任何 OpenAI 兼容接口，例如：

| 服务 | BASE_URL | MODEL 示例 |
|------|----------|------------|
| OpenAI | `https://api.openai.com/v1` | `gpt-4o` |
| 阿里百炼 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| 本地 Ollama | `http://localhost:11434/v1` | `llama3` |

- API Key 获取：参考所选服务商的官方文档
- Tavily API Key：注册 [https://tavily.com/](https://tavily.com/) 获取（免费额度足够测试）

### 第五步：启动服务

```bash
uvicorn main:app --reload --port 8000
```

服务启动后：
- API 服务：`http://localhost:8000`
- 交互式文档：`http://localhost:8000/docs`

**停止服务**：在终端按 `Ctrl+C`。

---

## API 使用示例

### 发送消息

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user_001",
    "message": "最近有哪些关于AI大模型的新闻？"
  }'
```

响应：

```json
{
  "session_id": "user_001",
  "reply": "根据最新搜索结果，近期AI大模型领域的重要动态包括..."
}
```

### 查询当前时间

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user_001",
    "message": "现在几点了？"
  }'
```

响应：

```json
{
  "session_id": "user_001",
  "reply": "当前日期是2026年04月07日，现在的时间是22:11:47。"
}
```

### 计算加法

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user_001",
    "message": "123.5加上456.5等于多少？"
  }'
```

响应：

```json
{
  "session_id": "user_001",
  "reply": "123.5 + 456.5 = 580.0"
}
```

### 超出能力范围

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user_001",
    "message": "帮我写一首诗"
  }'
```

响应：

```json
{
  "session_id": "user_001",
  "reply": "抱歉，我目前只能帮您搜索资讯、查询当前时间，或计算两个数的和，无法处理其他请求。"
}
```

### 清除会话记忆

```bash
curl -X DELETE http://localhost:8000/chat/user_001
```

响应：

```json
{
  "message": "会话 user_001 的记忆已清除"
}
```

---

## 设计与实现手记

### 技术选型

**为什么选择 FastAPI？**

FastAPI 基于 Python 类型注解自动生成请求/响应校验和 OpenAPI 文档，对于以 API 为核心的 Agent 服务而言，开发效率高、代码量少。相比 Flask，FastAPI 原生支持异步，更适合 I/O 密集型场景（如调用外部 LLM API 和搜索 API）。相比 Django，它更轻量，不引入不必要的 ORM 和模板层。

**为什么没有使用数据库？**

本项目的会话记忆是请求级的临时状态，用 Python 内存字典（`dict`）存储足以满足演示需求，零依赖、零配置。引入 Redis 或数据库会增加部署复杂度，在验证 Agent 核心逻辑的阶段属于过度设计。

**为什么选择任意 OpenAI 兼容 LLM？**

通过将 `BASE_URL`、`MODEL`、`API_KEY` 全部提取到环境变量，项目与具体服务商解耦。无论是 OpenAI、阿里百炼、DeepSeek，还是本地运行的 Ollama，只需修改 `.env` 即可切换，无需改动任何代码。选用的模型只需支持 function calling 能力即可正常工作。

---

### 核心实现：Agent 的决策逻辑

本项目使用 **ReAct（Reasoning + Acting）** 模式实现 Agent 循环：

```
用户输入
  → 拼接系统提示 + 会话历史
  → 调用 LLM（附带工具定义列表）
      ├── 模型返回 tool_calls → 执行对应工具 → 将结果追加到上下文 → 再次调用 LLM
      └── 模型返回普通文本 → 作为最终回复返回给用户
```

**关键实现细节：`reasoning_content` 的处理**

阿里百炼的 Qwen 系列模型在思考模式下，API 响应中会额外携带 `reasoning_content` 字段（模型的内部推理过程）。如果直接将 SDK 返回的消息对象追加到 `messages` 列表中，再次请求时 API 会因为识别不到 `reasoning_content` 字段而报错或行为异常。

解决方案是在将 assistant 消息追加到上下文前，手动将其转换为只包含标准字段（`role`、`content`、`tool_calls`）的字典：

```python
messages.append({
    "role": message.role,
    "content": message.content,
    "tool_calls": [
        {
            "id": tc.id,
            "type": tc.type,
            "function": {"name": tc.function.name, "arguments": tc.function.arguments},
        }
        for tc in message.tool_calls
    ],
})
```

**能力边界的实现**

通过系统提示明确约束模型只能使用已注册的三种工具，并规定当用户需求超出工具范围时返回固定提示语。这样无需在代码层面做额外判断，由 LLM 自身完成意图识别和边界控制。

---

### 权衡与展望

**当前实现的局限性**

| 局限 | 说明 |
|------|------|
| 会话记忆不持久 | 存在内存中，服务重启后所有会话历史丢失 |
| 无并发隔离 | 多请求同时修改同一 session 的历史时存在竞态风险 |
| 无认证机制 | API 完全公开，任何人可调用 |
| 搜索质量依赖第三方 | Tavily 的结果质量和可用性不受控 |
| 历史无上限 | 长会话会导致 token 消耗线性增长，最终超出模型上下文窗口 |

**如果要支撑百万级用户，架构调整方向**

1. **会话持久化**：将 `_sessions` 字典替换为 Redis，支持分布式部署和会话过期自动清理。

2. **异步化**：将 `agent.chat()` 改为 `async def`，LLM 和搜索 API 的 HTTP 请求改用 `httpx` 异步客户端，充分利用 FastAPI 的异步能力，大幅提升并发吞吐量。

3. **流式响应**：接入 LLM 的 streaming 模式，通过 SSE 或 WebSocket 将回复逐字推送给前端，改善用户体验。

4. **历史截断策略**：对超长会话自动保留最近 N 轮对话，或对历史进行摘要压缩，控制 token 消耗。

5. **网关与限流**：在服务前增加 API 网关（如 Kong 或 Nginx），实现身份认证、按用户限流、请求日志采集。

6. **可观测性**：接入链路追踪（如 OpenTelemetry），记录每次工具调用的耗时和结果，便于定位性能瓶颈。
