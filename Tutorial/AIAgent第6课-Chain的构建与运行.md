# AIAgent 项目实战课程 · 第 6 课详细讲义（二）

# Chain 的构建与运行

> 课程基于 `AgentProject/super_biz_agent_py-release-2026-05-17` 项目
> 学习方式：理论 + 代码解读 + 动手实验
> 前置知识：Model / Prompt / Output Parser（第 6 课第一部分）

---

## 1. 本课目标

通过本课学习，你能够：

- 说清楚 **Chain 的本质**：把多个组件按顺序组合成工作流
- 理解 **Legacy Chain** 与 **LCEL Chain** 的区别
- 掌握 **LCEL 管道语法**：`prompt | llm | parser`
- 熟练使用 `invoke`、`stream`、`batch`、`ainvoke`、`astream` 运行链
- 理解 **Runnable 接口** 与常见 **Runnable 组件**
- 能够在链中插入自定义函数（`RunnableLambda`）
- 理解同步调用与异步调用的适用场景

---

## 2. 什么是 Chain

### 2.1 生活中的"流水线"

想象一个披萨店：

```
面团 --> 加酱料 --> 加配料 --> 烘烤 --> 切块 --> 上桌
```

每个步骤只做一件事，上一步的输出作为下一步的输入。

Chain 就是 LangChain 里的 **流水线**：把 Model、Prompt、Parser、函数等组件串起来，每一步的输出作为下一步的输入，最终得到结果。

### 2.2 Chain 的核心价值

| 价值 | 说明 |
|------|------|
| **组件复用** | Prompt、Model、Parser 可以独立定义，多处复用 |
| **逻辑清晰** | 数据流向一目了然 |
| **易于测试** | 可以单独测试每个组件 |
| **支持流式** | 整个链可以流式运行 |
| **支持异步** | 适合 FastAPI 等异步框架 |
| **可观测性** | 可以在链中插入回调，记录中间状态 |

### 2.3 Chain 与直接调用 LLM 的区别

**直接调用 LLM**：

```python
response = llm.invoke("请用一句话介绍 FastAPI")
answer = response.content
```

**使用 Chain**：

```python
chain = prompt | llm | parser
answer = chain.invoke({"topic": "FastAPI"})
```

后者把提示词工程、模型调用、输出解析封装在一起，调用方只关心输入和输出。

---

## 3. Legacy Chain（了解即可）

### 3.1 旧式 Chain 类

在 LangChain 早期版本中，Chain 是通过类来构建的：

```python
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(...)
prompt = PromptTemplate.from_template("请用一句话介绍 {topic}")

chain = LLMChain(llm=llm, prompt=prompt)
result = chain.invoke({"topic": "FastAPI"})
print(result["text"])
```

还有 `SimpleSequentialChain`、`SequentialChain`、`RetrievalQA` 等。

### 3.2 为什么不推荐再用 Legacy Chain

| 问题 | 说明 |
|------|------|
| 接口不统一 | 每个 Chain 类的输入输出格式不同 |
| 难以组合 | 链与链之间拼接困难 |
| 流式支持差 | 很多旧 Chain 不支持流式输出 |
| 异步支持差 | 很多旧 Chain 没有 `ainvoke` |
| 官方已转向 LCEL | 新功能基本都在 LCEL 上实现 |

> 项目代码中已经没有 `LLMChain` 等旧式用法，全部使用 LCEL。本课提到 Legacy Chain 只是为了让你看到别人旧代码时能理解。

---

## 4. LCEL Chain 的构建

### 4.1 LCEL 是什么

**LCEL** = LangChain Expression Language，一种用 **管道符 `|`** 组合组件的声明式语法。

核心思想：

```
输入 --> 组件 A --> 组件 B --> 组件 C --> 输出
```

在代码里写成：

```python
chain = component_a | component_b | component_c
```

### 4.2 最小 LCEL 链

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
import os

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一位 {role}。"),
    ("human", "请用一句话介绍 {topic}"),
])

llm = ChatOpenAI(
    model="qwen-max",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.environ["DASHSCOPE_API_KEY"],
)

parser = StrOutputParser()

# LCEL 链
chain = prompt | llm | parser

result = chain.invoke({
    "role": "后端架构师",
    "topic": "LangChain"
})
print(result)
```

### 4.3 数据流解析

```
{"role": "后端架构师", "topic": "LangChain"}
           │
           ▼
    ┌──────────────┐
    │    prompt    │  -->  ChatPromptValue（消息列表）
    └──────────────┘
           │
           ▼
    ┌──────────────┐
    │     llm      │  -->  AIMessage
    └──────────────┘
           │
           ▼
    ┌──────────────┐
    │    parser    │  -->  str
    └──────────────┘
           │
           ▼
    "LangChain 是一个用于构建大模型应用的 Python 框架..."
```

每一步的输出类型，正好匹配下一步的输入类型：

- `ChatPromptTemplate.invoke(dict)` → `ChatPromptValue`
- `ChatOpenAI.invoke(ChatPromptValue)` → `AIMessage`
- `StrOutputParser.invoke(AIMessage)` → `str`

### 4.4 为什么 pipe 符号能工作

LangChain 给所有核心组件都实现了 `__or__` 方法，使它们支持 `|` 操作符。任何实现 `Runnable` 接口的对象都可以被 `|` 连接。

---

## 5. 运行 Chain 的五种方式

所有 LCEL Chain 都支持以下方法：

| 方法 | 说明 | 返回值 | 适用场景 |
|------|------|--------|---------|
| `invoke` | 单个输入同步调用 | 单个输出 | 普通接口 |
| `ainvoke` | 单个输入异步调用 | 单个输出 | FastAPI 接口 |
| `stream` | 单个输入流式调用 | 迭代器 | SSE 流式输出 |
| `astream` | 单个输入异步流式 | 异步迭代器 | 异步 SSE |
| `batch` | 批量输入同步调用 | 输出列表 | 批量处理 |
| `abatch` | 批量输入异步调用 | 输出列表 | 异步批量 |

### 5.1 invoke

```python
result = chain.invoke({"role": "后端架构师", "topic": "LangChain"})
print(result)
```

### 5.2 ainvoke

```python
result = await chain.ainvoke({"role": "后端架构师", "topic": "LangChain"})
print(result)
```

在 FastAPI 中：

```python
from fastapi import FastAPI
from langchain_core.runnables import RunnableSequence

app = FastAPI()

@app.post("/api/chat")
async def chat(req: ChatRequest):
    result = await chain.ainvoke({
        "role": "运维专家",
        "topic": req.question
    })
    return {"answer": result}
```

### 5.3 stream

```python
for chunk in chain.stream({"role": "后端架构师", "topic": "LangChain"}):
    print(chunk, end="", flush=True)
```

流式会逐个返回 `parser` 解析后的内容块。如果 parser 是 `StrOutputParser`，每个 chunk 就是字符串片段。

### 5.4 astream

```python
async for chunk in chain.astream({"role": "后端架构师", "topic": "LangChain"}):
    print(chunk, end="", flush=True)
```

这是项目 SSE 流式输出的核心机制。

### 5.5 batch

```python
inputs = [
    {"role": "后端架构师", "topic": "LangChain"},
    {"role": "运维专家", "topic": "Milvus"},
    {"role": "产品经理", "topic": "RAG"},
]
results = chain.batch(inputs)
for r in results:
    print(r)
```

`batch` 会自动并发，适合一次性处理多个独立请求。

---

## 6. Runnable 接口

### 6.1 什么是 Runnable

**Runnable** 是 `langchain-core` 定义的一个协议（protocol）。只要一个对象实现了 `invoke`、`stream`、`batch` 等方法，它就是 Runnable。

LangChain 中几乎所有核心组件都是 Runnable：

- `PromptTemplate` / `ChatPromptTemplate`
- `ChatOpenAI` / `ChatQwen`
- `StrOutputParser` / `PydanticOutputParser`
- `RunnableLambda` / `RunnablePassthrough` / `RunnableParallel`
- 由 `|` 组合出来的 Chain

### 6.2 Runnable 的通用接口

```python
chain.invoke(input)        # 同步单条
chain.ainvoke(input)       # 异步单条
chain.stream(input)        # 同步流式
chain.astream(input)       # 异步流式
chain.batch(inputs)        # 同步批量
chain.abatch(inputs)       # 异步批量
```

### 6.3 查看 Chain 的输入输出 Schema

```python
print(chain.get_input_schema().schema())
print(chain.get_output_schema().schema())
```

这在调试和写接口文档时很有用。

### 6.4 Runnable 的 `.with_config`

可以给 Runnable 附加运行时配置，例如标签、元数据：

```python
chain_with_meta = chain.with_config({"run_name": "intro_chain"})
```

后续结合 Callbacks 可以做更细粒度的监控。

---

## 7. 常用 Runnable 组件

### 7.1 RunnableLambda：把普通函数变成 Runnable

如果你想在链中插入自定义 Python 函数，用 `RunnableLambda`：

```python
from langchain_core.runnables import RunnableLambda

def add_greeting(input: dict) -> dict:
    input["greeting"] = "你好，"
    return input

greeting_step = RunnableLambda(add_greeting)

chain = greeting_step | prompt | llm | parser
```

注意：函数需要接收上一步的输出，并返回下一步能处理的输入。

### 7.2 RunnablePassthrough：透传输入

如果你想把输入原样传给下一步，同时再附加一些字段，用 `RunnablePassthrough`：

```python
from langchain_core.runnables import RunnablePassthrough

chain = RunnablePassthrough.assign(count=lambda x: len(x["topic"])) | prompt | llm | parser

result = chain.invoke({"role": "专家", "topic": "LangChain"})
```

`RunnablePassthrough.assign` 会在原字典基础上添加新字段。

### 7.3 RunnableParallel：并行执行多个分支

```python
from langchain_core.runnables import RunnableParallel

parallel = RunnableParallel(
    summary=summary_chain,
    keywords=keywords_chain,
)

result = parallel.invoke({"topic": "LangChain"})
print(result["summary"])
print(result["keywords"])
```

`RunnableParallel` 会同时运行多个分支，适合一个输入需要多种处理的场景。

### 7.4 RunnableBranch：条件分支

```python
from langchain_core.runnables import RunnableBranch

branch = RunnableBranch(
    (lambda x: x["language"] == "中文", chinese_chain),
    (lambda x: x["language"] == "英文", english_chain),
    default_chain,
)

result = branch.invoke({"language": "中文", "topic": "LangChain"})
```

`RunnableBranch` 会按顺序判断条件，第一个为 `True` 的分支会被执行。

### 7.5 RunnableSequence（隐式）

当你写 `a | b | c` 时，LangChain 内部会创建一个 `RunnableSequence`。也可以显式创建：

```python
from langchain_core.runnables import RunnableSequence

chain = RunnableSequence(
    first=prompt,
    middle=[llm],
    last=parser,
)
```

不过日常开发中直接用 `|` 更简洁。

---

## 8. Chain 的执行流程与类型传递

### 8.1 数据类型必须匹配

链能跑通的前提是：上一步的输出类型 = 下一步的输入类型。

```
PromptTemplate      输出 ChatPromptValue
ChatOpenAI          输入 ChatPromptValue，输出 AIMessage
StrOutputParser     输入 AIMessage，输出 str
```

如果类型不匹配，会报错。例如：

```python
# 错误示例：把 StrOutputParser 放在 LLM 前面
chain = prompt | parser | llm  # ❌ parser 输出 str，llm 期望 ChatPromptValue
```

### 8.2 输入可以是字典、字符串、消息列表

不同类型的 Runnable 接受不同类型的输入：

| Runnable | 典型输入 | 典型输出 |
|----------|---------|---------|
| `PromptTemplate` | `dict` | `StringPromptValue` |
| `ChatPromptTemplate` | `dict` | `ChatPromptValue` |
| `ChatOpenAI` | `str` 或 `list[BaseMessage]` 或 `ChatPromptValue` | `AIMessage` |
| `StrOutputParser` | `AIMessage` / `str` | `str` |
| `PydanticOutputParser` | `AIMessage` / `str` | Pydantic 对象 |

---

## 9. 调试 Chain

### 9.1 开启全局调试

```python
from langchain.globals import set_debug

set_debug(True)

chain.invoke({...})
```

开启后，LangChain 会打印每个 Runnable 的输入、输出和耗时。

### 9.2 单独测试每个组件

```python
# 测试 prompt
messages = prompt.invoke({"role": "专家", "topic": "LangChain"})
print(messages)

# 测试 llm
response = llm.invoke(messages)
print(response.content)

# 测试 parser
text = parser.invoke(response)
print(text)
```

把链拆成单步测试，是定位问题最快的方法。

### 9.3 查看链的图结构

```python
chain.get_graph().print_ascii()
```

可以可视化链的结构，复杂链尤其有用。

---

## 10. 常见错误与解决方案

### Q1：`AttributeError: 'str' object has no attribute 'content`

**原因**：把 `StrOutputParser` 放在了 LLM 前面，或者某个函数返回了字符串但下一步期望消息对象。

**解决**：检查链的顺序，确保输入输出类型匹配。

### Q2：`ValidationError` 来自 PydanticOutputParser

**原因**：模型没有按 JSON 格式输出，或 JSON 字段不符合模型定义。

**解决**：
- 确认 prompt 里包含 `format_instructions`
- 换更强的模型（如 `qwen-max`）
- 使用 `with_fallbacks` 添加容错

### Q3：链在 FastAPI 里阻塞

**原因**：用了 `chain.invoke()` 而不是 `chain.ainvoke()`。

**解决**：FastAPI 接口中统一使用异步方法。

### Q4：流式输出没有内容

**原因**：模型本身不支持流式，或前端没有正确消费 SSE。

**解决**：确认模型支持流式，并用 `chain.astream()` 或 `chain.stream()`。

---

## 11. 本课小结

通过本课学习，你应该已经掌握：

- Chain 的本质：把多个组件按顺序组合成工作流
- Legacy Chain 与 LCEL Chain 的区别
- 用 `|` 管道符构建 LCEL 链
- `invoke`、`ainvoke`、`stream`、`astream`、`batch`、`abatch` 的用法
- Runnable 接口与常见 Runnable 组件
- 如何在链中插入自定义函数
- 如何调试链和排查常见错误

### 下节预告

**第 6 课（三）：LCEL 入门与动手实验**

我们将通过多个实战示例，亲手搭建：

- 最简单的 `PromptTemplate → LLM → StrOutputParser` 链
- 结构化输出链
- 并行分支链
- 条件分支链

---

## 12. 参考资料

- [LangChain Expression Language (LCEL)](https://python.langchain.com/docs/concepts/lcel/)
- [LangChain Runnables 文档](https://python.langchain.com/docs/concepts/runnables/)
- [LangChain Core API - Runnable](https://api.python.langchain.com/en/stable/runnables_api_reference.html)
- [FastAPI 异步接口](https://fastapi.tiangolo.com/async/)

---

*生成时间：2026/06/30*  
*课程：AIAgent 项目实战 · 第 6 课（二）*
