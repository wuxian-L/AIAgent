# AIAgent 项目实战课程 · 第 6 课详细讲义（一）

# LangChain 概述与 Model / Prompt / Output Parser

> 课程基于 `AgentProject/super_biz_agent_py-release-2026-05-17` 项目
> 学习方式：理论 + 代码解读 + 动手实验
> 对应文件：`pyproject.toml` 中 LangChain 相关依赖

---

## 1. 本课目标

通过本课学习，你能够：

- 说清楚 **LangChain 的定位** 与 **核心解决的问题**
- 理解 LangChain 的 **版本分层**：`langchain-core`、`langchain`、`langchain-community`、partner packages
- 读懂项目 `pyproject.toml` 中 LangChain 依赖的设计意图
- 掌握 **Model I/O** 三大核心抽象：**Model（模型）**、**Prompt（提示词）**、**Output Parser（输出解析器）**
- 能够独立初始化一个 `ChatOpenAI` 模型实例（使用 DashScope OpenAI 兼容接口）
- 能够编写带变量的 `PromptTemplate` 和 `ChatPromptTemplate`
- 能够使用 `StrOutputParser` 和 `PydanticOutputParser` 解析模型输出
- 为下一节课学习 **Chain 与 LCEL** 打下基础

---

## 2. 前置知识回顾

| 知识点 | 要求 | 说明 |
|--------|------|------|
| Python 基础 | 掌握 | 类、函数、字典、类型注解 |
| Pydantic BaseModel | 掌握 | 第 5 课已学，用于数据校验 |
| FastAPI 基础 | 了解 | 知道路由、请求体、响应模型 |
| HTTP / API | 了解 | 知道如何通过 HTTP 调用大模型接口 |
| 环境变量 | 了解 | 知道 `.env`、API Key 的基本用法 |

如果你还没看过第 5 课，建议先回顾 **Pydantic `BaseModel`** 和 **pydantic-settings**，因为 LangChain 的输出解析大量依赖 Pydantic。

---

## 3. 为什么需要 LangChain

### 3.1 直接调用大模型 API 的痛点

假设我们只用一个 HTTP 客户端调用大模型：

```python
import requests

response = requests.post(
    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    headers={"Authorization": "Bearer sk-xxx"},
    json={
        "model": "qwen-max",
        "messages": [{"role": "user", "content": "请用一句话介绍 FastAPI"}]
    }
)
answer = response.json()["choices"][0]["message"]["content"]
print(answer)
```

这种方式的问题：

| 问题 | 说明 |
|------|------|
| 每次都要手写 HTTP 请求 | 重复且容易出错 |
| 提示词管理混乱 | 提示词直接写在代码字符串里，难以复用和维护 |
| 输出格式不稳定 | 模型返回纯文本，需要自己解析 JSON / 结构化数据 |
| 没有组件化思想 | 模型、提示词、解析器耦合在一起 |
| 切换模型成本高 | 从 DashScope 切到 OpenAI 要重写请求体 |
| 缺少工具调用、记忆、检索等能力 | 复杂 Agent 难以直接实现 |

### 3.2 LangChain 解决什么问题

LangChain 是一套 **LLM 应用开发框架**，它把大模型应用开发中反复出现的模式抽象成可复用的组件：

- **Model I/O**：统一不同 LLM 的调用方式
- **Prompt 管理**：模板化、参数化提示词
- **Output Parsing**：把模型输出解析成结构化数据
- **Chains**：把多个组件串成工作流
- **Retrieval**：连接向量数据库，实现 RAG
- **Agents**：让模型自主决定调用哪些工具
- **Memory / Callbacks**：会话记忆与可观测性

用 LangChain 后，上面的代码可以写成：

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="qwen-max",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-xxx",
)
answer = llm.invoke("请用一句话介绍 FastAPI")
print(answer.content)
```

后续还可以把提示词、模型、解析器串成一条 **Chain**，代码更清晰、更容易维护。

---

## 4. LangChain 是什么

### 4.1 官方定义

LangChain 是一个用于开发由语言模型驱动的应用程序的框架。它提供：

1. **组件化抽象**：把 LLM 应用拆成模型、提示词、解析器、检索器、工具等独立组件
2. **组合机制**：通过 LCEL（LangChain Expression Language）把组件组合成复杂工作流
3. **生态集成**：与 OpenAI、Anthropic、阿里云 DashScope、Milvus、FastAPI 等无缝集成

### 4.2 版本分层与项目依赖

打开项目 `pyproject.toml`，LangChain 相关依赖如下：

```toml
dependencies = [
    "langchain>=0.1.0",
    "langchain-community>=0.0.20",
    "langchain-core>=0.1.0",
    "langchain-openai>=1.0.0",
    "langgraph>=0.0.40",
    "langchain-milvus>=0.3.3",
    "langchain-text-splitters>=1.1.0",
    "langchain-mcp-adapters>=0.2.1",
    "langchain-qwq>=0.3.4",
]
```

这些包的分层含义：

| 包名 | 作用 | 是否必须 |
|------|------|---------|
| `langchain-core` | 提供最基础的接口：`BaseLanguageModel`、`BasePromptTemplate`、`Runnable`、`BaseMessage` 等 | ✅ 核心 |
| `langchain` | 官方维护的高层组件和 Chain 实现 | ✅ 常用 |
| `langchain-community` | 社区贡献的第三方集成（如文档加载器、向量库） | ✅ 项目需要 |
| `langchain-openai` | OpenAI / OpenAI 兼容接口的官方 partner 包 | ✅ 项目用 DashScope 兼容模式 |
| `langchain-qwq` | 阿里云 QwQ / Qwen 原生接口 | ✅ 项目后续课程使用 |
| `langchain-milvus` | Milvus 向量数据库集成 | ✅ RAG 课程 |
| `langchain-text-splitters` | 文档切分工具 | ✅ RAG 课程 |
| `langchain-mcp-adapters` | MCP 协议适配器 | ✅ Agent / MCP 课程 |
| `langgraph` | 构建复杂状态图和 Agent 工作流 | ✅ Agent / AIOps 课程 |

### 4.3 为什么分层

LangChain 从 v0.1 开始把核心接口拆到 `langchain-core`，把具体集成拆到 partner packages。好处是：

- **解耦**：核心接口稳定，第三方集成可以独立迭代
- **按需安装**：不需要把所有集成都装进来
- **避免循环依赖**：社区包更新不会破坏核心接口
- **类型安全**：`langchain-core` 定义了统一的 `Runnable` 协议

我们在写代码时，通常从 `langchain_core` 导入基础抽象，从 `langchain_xxx` 导入具体实现。

---

## 5. LangChain 核心架构

### 5.1 六大模块

```
┌─────────────────────────────────────────────────────────────────┐
│                        LangChain 应用                            │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────┤
│  Model I/O  │  Retrieval  │    Chains   │   Agents    │ Memory  │
│             │             │             │             │         │
│  Model      │  Loaders    │  Chain      │  Tools      │  History│
│  Prompt     │  Splitters  │  LCEL       │  ReAct      │  Trim   │
│  Parser     │  Embeddings │  Runnable   │  PlanExec   │         │
│             │  VectorStore│             │             │         │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   Callbacks 回调   │
                    │  日志 / 追踪 / 监控  │
                    └───────────────────┘
```

### 5.2 模块与本课程/项目的对应关系

| 模块 | 本课覆盖 | 项目中对应 |
|------|---------|-----------|
| **Model I/O** | ✅ 本课 | `app/core/llm_factory.py`、`app/services/rag_agent_service.py` |
| **Retrieval** | 第 10-15 课 | `app/services/document_splitter_service.py`、`app/services/vector_store_manager.py` |
| **Chains** | ✅ 本课 / 第 6-7 课 | `app/services/rag_agent_service.py` 中的链式调用 |
| **Agents** | 第 16-20 课 | `app/services/rag_agent_service.py` 中的 Agent |
| **Memory** | 第 9、28 课 | `app/services/rag_agent_service.py` 中的消息修剪 |
| **Callbacks** | 第 26 课 | `app/utils/logger.py`、Loguru 集成 |

本课只聚焦 **Model I/O**，这是进入 LangChain 世界的第一步。

---

## 6. Model I/O 概览

Model I/O 是 LangChain 最基础的概念，包含三个核心抽象：

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   用户输入   │ --> │   Prompt    │ --> │    Model    │ --> │ OutputParser│
│   "..."     │     │  提示词模板   │     │   大模型     │     │  输出解析器   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       Input              Format             Predict              Parse
```

| 抽象 | 作用 | 示例类 |
|------|------|--------|
| **Prompt** | 把用户输入格式化成模型能理解的文本或消息 | `PromptTemplate`、`ChatPromptTemplate` |
| **Model** | 调用大模型，返回文本或消息 | `ChatOpenAI`、`ChatQwen` |
| **Output Parser** | 把模型输出解析成目标格式 | `StrOutputParser`、`PydanticOutputParser` |

这三个组件可以独立使用，也可以通过 `|` 管道符组合成 Chain。

---

## 7. Model：模型

### 7.1 LLM 与 Chat Model 的区别

LangChain 把模型分成两类：

| 类型 | 输入 | 输出 | 代表类 | 适用场景 |
|------|------|------|--------|---------|
| **LLM** | 字符串 | 字符串 | `OpenAI`、`HuggingFacePipeline` | 补全、生成类任务 |
| **Chat Model** | 消息列表 | 消息 | `ChatOpenAI`、`ChatQwen` | 对话、Agent、工具调用 |

现代大模型（GPT-4、Claude、Qwen、DeepSeek）基本都是 **Chat Model**，项目中也统一使用 Chat Model。

### 7.2 项目使用的 Chat Model

项目中有两种接入方式：

1. **OpenAI 兼容模式**：通过 `langchain_openai.ChatOpenAI` 调用 DashScope
2. **原生模式**：通过 `langchain_qwq.ChatQwen` 调用阿里云 Qwen / QwQ

本课先学习 **OpenAI 兼容模式**，因为它通用、稳定，也是第 7 课 LLM 工厂的基础。

### 7.3 初始化 ChatOpenAI（DashScope 兼容）

```python
import os
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="qwen-max",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.environ["DASHSCOPE_API_KEY"],
    temperature=0.7,
)

response = llm.invoke("请用一句话介绍 FastAPI")
print(response.content)
```

关键参数说明：

| 参数 | 说明 | 项目取值 |
|------|------|---------|
| `model` | 模型名称 | `"qwen-max"` / `"qwen-turbo"` |
| `base_url` | OpenAI 兼容接口地址 | `"https://dashscope.aliyuncs.com/compatible-mode/v1"` |
| `api_key` | API Key | 从 `.env` 的 `DASHSCOPE_API_KEY` 读取 |
| `temperature` | 随机性，0-2 | 0 更确定，1 更有创意 |
| `max_tokens` | 最大生成 token 数 | 按需设置 |
| `model_kwargs` | 透传给模型的额外参数 | 如 `{"top_p": 0.9}` |

### 7.4 返回值：AIMessage

`llm.invoke(...)` 返回的是一个 `AIMessage` 对象：

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(...)
response = llm.invoke("你好")
print(type(response))
# <class 'langchain_core.messages.ai.AIMessage'>

print(response.content)
# 你好！有什么可以帮你的吗？
```

`AIMessage` 属于 LangChain 的 **Message** 类型，后续课程会详细讲。这里只需要知道：

- `.content`：获取模型返回的文本内容
- `.response_metadata`：包含 token 用量、模型名等元信息
- `.tool_calls`：如果模型调用了工具，会在这里（Agent 课程讲）

### 7.5 同步与异步调用

Chat Model 支持同步和异步：

```python
# 同步
response = llm.invoke("你好")

# 异步
response = await llm.ainvoke("你好")
```

FastAPI 的接口都是异步的，所以项目中大量使用 `ainvoke`。

### 7.6 流式输出

Chat Model 也支持流式输出，适合前端逐字显示：

```python
for chunk in llm.stream("请写一首关于夏天的诗"):
    print(chunk.content, end="", flush=True)
```

流式返回的是 `AIMessageChunk`，每个 chunk 只有一部分内容。

### 7.7 批量调用

如果有多个独立输入，可以用 `batch` 一次性调用：

```python
inputs = ["什么是 RAG？", "什么是 Agent？", "什么是 MCP？"]
responses = llm.batch(inputs)
for r in responses:
    print(r.content)
```

`batch` 会自动做并发优化，比循环 `invoke` 效率更高。

---

## 8. Prompt：提示词

### 8.1 为什么需要 Prompt Template

直接把用户问题传给模型，控制能力很弱。实际应用中，我们通常需要：

- 给模型设定角色（System Prompt）
- 把用户输入嵌入到固定模板中
- 保留对话历史
- 动态插入外部上下文

**Prompt Template** 就是用来解决这些问题的。

### 8.2 PromptTemplate（字符串模板）

适用于单轮文本补全类任务：

```python
from langchain_core.prompts import PromptTemplate

template = PromptTemplate.from_template(
    "请用 {style} 的语气，向 {audience} 解释 {topic}。"
)

prompt_value = template.invoke({
    "style": "轻松",
    "audience": "小学生",
    "topic": "向量数据库"
})

print(prompt_value.to_string())
# 请用 轻松 的语气，向 小学生 解释 向量数据库。
```

`PromptTemplate` 的核心是 **变量替换**：用 `{variable}` 占位，调用时传入字典。

### 8.3 ChatPromptTemplate（消息模板）

Chat Model 的输入是 **消息列表**，所以更常用 `ChatPromptTemplate`：

```python
from langchain_core.prompts import ChatPromptTemplate

template = ChatPromptTemplate.from_messages([
    ("system", "你是一位 {role}，擅长用简洁的语言回答技术问题。"),
    ("human", "请解释什么是 {topic}？"),
])

messages = template.invoke({
    "role": "资深后端工程师",
    "topic": "FastAPI"
})

print(messages)
```

输出：

```
SystemMessage(content='你是一位 资深后端工程师，擅长用简洁的语言回答技术问题。')
HumanMessage(content='请解释什么是 FastAPI？')
```

`from_messages` 支持的元组格式：

| 元组 | 说明 |
|------|------|
| `("system", "...")` | 系统消息，设定模型角色和行为 |
| `("human", "...")` | 人类/用户消息 |
| `("ai", "...")` | AI 助手的回复，可用于 few-shot 示例 |
| `("placeholder", "{messages}")` | 占位符，后续插入消息历史 |

### 8.4 使用 MessagesPlaceholder 插入历史

在对话场景中，我们需要把历史消息插入到模板中：

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

template = ChatPromptTemplate.from_messages([
    ("system", "你是一位运维专家。"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])

messages = template.invoke({
    "history": [
        ("human", "服务器 CPU 高了怎么办？"),
        ("ai", "可以先查看 top 命令，定位高 CPU 进程。"),
    ],
    "question": "怎么定位具体是哪个服务？"
})
```

`MessagesPlaceholder` 会在指定位置展开 `history` 列表，这是实现多轮对话记忆的关键。

### 8.5 提示词的最佳实践

| 建议 | 说明 |
|------|------|
| 用 System Prompt 设定角色 | 让模型知道它是谁、该做什么 |
| 任务描述要具体 | 越具体，输出越可控 |
| 给出示例（few-shot） | 对格式要求高的场景非常有效 |
| 输出格式单独说明 | 如果要用 parser，务必在提示词里写清楚格式要求 |
| 避免过长的提示词 | 会占用上下文窗口，影响推理质量 |

---

## 9. Output Parser：输出解析器

### 9.1 为什么需要 Output Parser

大模型返回的是文本，但程序通常需要结构化数据。例如：

```json
{
  "root_cause": "数据库连接池耗尽",
  "recommendations": ["扩容连接池", "优化慢 SQL"]
}
```

Output Parser 的作用就是 **把文本转成结构化数据**，并与 Pydantic 模型集成。

### 9.2 StrOutputParser（字符串解析器）

最简单的解析器，直接返回 `.content` 字符串：

```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()

# 传入 AIMessage
result = parser.invoke(response)
print(result)
# 你好！有什么可以帮你的吗？
```

`StrOutputParser` 常用于最终输出给用户的场景。

### 9.3 PydanticOutputParser（结构化解析器）

当需要把模型输出解析成 Pydantic 对象时，用这个解析器。

#### 步骤 1：定义 Pydantic 模型

```python
from pydantic import BaseModel, Field

class Diagnosis(BaseModel):
    root_cause: str = Field(description="故障根因")
    recommendations: list[str] = Field(description="修复建议列表")
```

#### 步骤 2：创建解析器并获取格式说明

```python
from langchain_core.output_parsers import PydanticOutputParser

parser = PydanticOutputParser(pydantic_object=Diagnosis)
format_instructions = parser.get_format_instructions()
print(format_instructions)
```

`format_instructions` 是一段自动生成的提示，告诉模型必须输出 JSON，并给出 schema。

#### 步骤 3：把格式说明写入 Prompt

```python
from langchain_core.prompts import PromptTemplate

template = PromptTemplate.from_template(
    """请根据以下故障现象给出诊断结果。

故障现象：{symptom}

{format_instructions}
"""
)

prompt_value = template.invoke({
    "symptom": "数据库 CPU 使用率持续 95% 以上",
    "format_instructions": format_instructions,
})
```

#### 步骤 4：调用模型并解析

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(...)
response = llm.invoke(prompt_value)
diagnosis = parser.invoke(response)
print(diagnosis.root_cause)
print(diagnosis.recommendations)
```

### 9.4 PydanticOutputParser 的注意事项

| 注意点 | 说明 |
|--------|------|
| 提示词必须包含 `format_instructions` | 否则模型不知道要输出 JSON |
| 模型能力要足够 | 小模型可能不遵守格式要求 |
| 失败时可以重试 | LangChain 提供 `RetryOutputParser` |
| 更复杂场景可用 `with_structured_output` | 后续课程会讲 |

### 9.5 解析失败怎么办

```python
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda

parser = PydanticOutputParser(pydantic_object=Diagnosis)

# 如果解析失败，可以 fallback 到字符串
safe_parser = parser.with_fallbacks([RunnableLambda(lambda x: {"raw": x.content})])
```

这种 **fallback** 机制在生产环境中很有用，避免因为一个格式错误就导致整个链路失败。

---

## 10. Model / Prompt / Parser 的组合

虽然还没有正式讲 Chain，但可以先看一个最小组合：

```python
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. 模型
llm = ChatOpenAI(
    model="qwen-max",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.environ["DASHSCOPE_API_KEY"],
)

# 2. 提示词模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一位 {role}。"),
    ("human", "请用一句话介绍 {topic}"),
])

# 3. 输出解析器
parser = StrOutputParser()

# 4. 组合成链（下节课详细讲）
chain = prompt | llm | parser

# 5. 运行
result = chain.invoke({
    "role": "后端架构师",
    "topic": "LangChain"
})
print(result)
```

这就是 LCEL 的雏形：`prompt | llm | parser`。下节课会详细拆解。

---

## 11. 本课小结

通过本课学习，你应该已经掌握：

- LangChain 的定位：LLM 应用开发框架
- LangChain 的版本分层：`langchain-core`、partner packages
- 项目 `pyproject.toml` 中各 LangChain 包的作用
- Model I/O 三大核心抽象：Model、Prompt、Output Parser
- 如何用 `ChatOpenAI` 调用 DashScope 兼容接口
- `PromptTemplate` 与 `ChatPromptTemplate` 的用法
- `MessagesPlaceholder` 在对话模板中的作用
- `StrOutputParser` 与 `PydanticOutputParser` 的用法
- 如何把三者组合成一条简单链

### 下节预告

**第 6 课（二）：Chain 的构建与运行**

我们将学习：

- Chain 的本质与两种写法
- LCEL 链的构建与运行方式
- `invoke`、`stream`、`batch` 的区别
- `Runnable` 接口与常用 `Runnable` 组件

---

## 12. 参考资料

- [LangChain 官方文档](https://python.langchain.com/)
- [LangChain Core API](https://api.python.langchain.com/en/stable/core_api_reference.html)
- [LangChain OpenAI 集成](https://python.langchain.com/docs/integrations/chat/openai/)
- [阿里云 DashScope OpenAI 兼容接口](https://help.aliyun.com/zh/dashscope/developer-reference/compatibility-of-openai-with-dashscope)
- [Pydantic 官方文档](https://docs.pydantic.dev/)

---

*生成时间：2026/06/30*  
*课程：AIAgent 项目实战 · 第 6 课（一）*
