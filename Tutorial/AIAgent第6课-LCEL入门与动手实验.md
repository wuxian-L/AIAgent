# AIAgent 项目实战课程 · 第 6 课详细讲义（三）

# LCEL 入门与动手实验

> 课程基于 `AgentProject/super_biz_agent_py-release-2026-05-17` 项目
> 学习方式：理论 + 代码解读 + 动手实验
> 前置知识：Model I/O（第 6 课一）、Chain 构建（第 6 课二）

---

## 1. 本课目标

通过本课学习，你能够：

- 独立搭建 **PromptTemplate → LLM → StrOutputParser** 的完整 LCEL 链
- 独立搭建 **结构化输出链**（模型输出 → Pydantic 对象）
- 理解 **RunnableParallel** 的实际用法：一个输入、多个输出
- 理解 **RunnableBranch** 的实际用法：按条件选择不同执行路径
- 初步体验 Chain 的 **流式输出**
- 能够把学到的 Chain 能力用到项目的真实场景中

---

## 2. 实验环境准备

### 2.1 安装依赖

如果还没安装，执行：

```bash
pip install langchain langchain-openai python-dotenv
```

### 2.2 准备 API Key

创建一个实验脚本 `langchain_lab.py`，放在项目根目录：

```python
import os
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 中的环境变量

DASHSCOPE_API_KEY = os.environ["DASHSCOPE_API_KEY"]
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

print(f"API Key 已加载：{DASHSCOPE_API_KEY[:10]}...")
```

### 2.3 创建共享的 LLM 实例

为了后续实验复用，先在脚本里创建一个公共的 LLM 实例：

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="qwen-max",
    base_url=DASHSCOPE_BASE_URL,
    api_key=DASHSCOPE_API_KEY,
    temperature=0.7,
)
```

---

## 3. 实验 1：最简单的 LCEL 链

### 3.1 目标

搭建 `PromptTemplate → LLM → StrOutputParser` 链，体验最基础的 LangChain 工作流。

### 3.2 代码

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. 定义提示词模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一位 {role}，用 {style} 的风格回答问题。"),
    ("human", "{question}"),
])

# 2. 定义输出解析器
parser = StrOutputParser()

# 3. 组合成链
chain = prompt | llm | parser

# 4. 运行
result = chain.invoke({
    "role": "Linux 运维专家",
    "style": "简洁专业",
    "question": "服务器磁盘使用率达到 95%，应该如何排查？"
})

print("=" * 60)
print("回答：")
print(result)
print("=" * 60)
```

### 3.3 预期输出

```
============================================================
回答：
1. 执行 df -h 查看分区占用情况。
2. 使用 du -sh /* 逐层定位是大目录或大文件。
3. 检查日志 /var/log 和临时文件 /tmp。
4. 清理无用文件，必要时扩容磁盘。
============================================================
```

### 3.4 理解数据流

```
{"role": "Linux 运维专家", "style": "简洁专业", "question": "..."}  # dict
    │
    ▼ prompt.invoke()
ChatPromptValue(messages=[SystemMessage(...), HumanMessage(...)])
    │
    ▼ llm.invoke()
AIMessage(content="1. 执行 df -h ...")
    │
    ▼ parser.invoke()
"1. 执行 df -h ..."  # str
```

### 3.5 验证不同输入的表现

```python
# 尝试不同的 role 和 style
results = chain.batch([
    {"role": "幼儿园老师", "style": "生动活泼", "question": "什么是云服务器？"},
    {"role": "大学教授", "style": "严谨学术", "question": "什么是云服务器？"},
    {"role": "脱口秀演员", "style": "幽默风趣", "question": "什么是云服务器？"},
])

for i, r in enumerate(results):
    print(f"\n--- 回答 {i+1} ---")
    print(r[:200], "...")
```

观察同一问题用不同角色和风格回答的巨大差异——这正是 Prompt Engineering 的威力。

### 3.6 流式输出版本

```python
print("流式输出：\n")
for chunk in chain.stream({
    "role": "Python 技术作家",
    "style": "通俗易懂",
    "question": "解释什么是异步编程"
}):
    print(chunk, end="", flush=True)
print()
```

观察流式输出和一次性输出在用户体验上的差异。

---

## 4. 实验 2：结构化输出链

### 4.1 目标

LLM 输出 → 解析成 Pydantic 对象 → 程序可以安全地使用 `.字段名` 访问。

### 4.2 步骤一：定义 Pydantic 模型

```python
from pydantic import BaseModel, Field

class AlertDiagnosis(BaseModel):
    """告警诊断结果"""
    severity_level: str = Field(description="严重程度：critical / warning / info")
    root_cause: str = Field(description="根因分析，不超过 100 字")
    affected_services: list[str] = Field(description="受影响的服务列表")
    recommendations: list[str] = Field(description="修复建议，至少 2 条")
    need_manual_intervention: bool = Field(description="是否需要人工介入")
```

### 4.3 步骤二：创建解析器并获取格式说明

```python
from langchain_core.output_parsers import PydanticOutputParser

parser = PydanticOutputParser(pydantic_object=AlertDiagnosis)
format_instructions = parser.get_format_instructions()
print("格式说明：")
print(format_instructions)
```

你会看到类似这样的输出：

```
The output should be formatted as a JSON instance that conforms to the JSON schema below.

{
  "properties": {
    "severity_level": {
      "description": "严重程度：critical / warning / info",
      "type": "string"
    },
    ...
  },
  "required": [...]
}
```

### 4.4 步骤三：构建链

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一位资深运维专家。请根据告警信息进行诊断。

{format_instructions}

请严格按 JSON 格式输出，不要输出其他内容。"""),
    ("human", """告警信息如下：
- 告警名称：{alert_name}
- 告警描述：{alert_description}
- 告警实例：{alert_instance}
- 持续时长：{alert_duration}"""),
])

chain = prompt | llm | parser
```

### 4.5 步骤四：运行并验证

```python
result = chain.invoke({
    "format_instructions": format_instructions,
    "alert_name": "HighCPUUsage",
    "alert_description": "生产环境数据库服务器 CPU 使用率持续超过 95%",
    "alert_instance": "db-prod-01.example.com",
    "alert_duration": "30 分钟",
})

print("类型：", type(result))
print("严重程度：", result.severity_level)
print("根因：", result.root_cause)
print("受影响服务：", result.affected_services)
print("修复建议：")
for r in result.recommendations:
    print(f"  - {r}")
print("需要人工介入：", result.need_manual_intervention)
```

### 4.6 类型安全的好处

解析后是 Pydantic 对象，IDE 有智能提示，字段访问有类型校验：

```python
# ✅ 类型安全
print(result.root_cause)        # str
print(result.recommendations)   # list[str]

# ❌ 如果用 StrOutputParser，这些都是字符串
# text = chain.invoke(...)
# print(text["root_cause"])  # TypeError: string indices must be integers
```

---

## 5. 实验 3：并行分支链

### 5.1 目标

一条输入同时送给多个处理分支，每个分支从不同角度分析，最后汇总。

### 5.2 场景

运维团队收到一条告警，需要同时做：
- **摘要**：用一句话概括告警
- **分类**：判断告警类型（CPU / 磁盘 / 网络 / 应用）
- **紧急度**：评估是否需要立即处理

### 5.3 定义三个子链

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def make_chain(system_prompt, question_template):
    """创建一条简单的子链"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{alert}"),
    ])
    return prompt | llm | StrOutputParser()

summary_chain = make_chain(
    "你是一位运维工程师。请用一句话概括这条告警的核心问题。",
    "告警内容：{alert}"
)

category_chain = make_chain(
    "你是一位运维分类专家。只输出一个词：CPU/磁盘/网络/应用/其他。",
    "告警内容：{alert}"
)

urgency_chain = make_chain(
    "你是一位值班主管。只回答：紧急/关注/已知。",
    "告警内容：{alert}"
)
```

### 5.4 组合成并行链

```python
from langchain_core.runnables import RunnableParallel

parallel_chain = RunnableParallel(
    summary=summary_chain,
    category=category_chain,
    urgency=urgency_chain,
)
```

### 5.5 运行

```python
alert_text = "数据库服务器 db-prod-01 CPU 使用率 98%，已持续 30 分钟，主从同步延迟增加"

result = parallel_chain.invoke({"alert": alert_text})

print("摘要：", result["summary"])
print("分类：", result["category"])
print("紧急度：", result["urgency"])
```

### 5.6 理解并行执行

```
              ┌─── summary_chain ───► "数据库 CPU 持续高负载，同步延迟升高"
              │
{"alert": "..."}
              ├─── category_chain ──► "CPU"
              │
              └─── urgency_chain ───► "紧急"
```

三条子链**同时执行**，不需要等待上一链完成。对于 IO 密集型的 LLM 调用，并行能显著减少总耗时。

### 5.7 对比异步与非并行串行

```python
import time

# 并行
start = time.time()
parallel_chain.invoke({"alert": alert_text})
print(f"并行耗时：{time.time() - start:.1f} 秒")

# 串行
start = time.time()
s = summary_chain.invoke({"alert": alert_text})
c = category_chain.invoke({"alert": alert_text})
u = urgency_chain.invoke({"alert": alert_text})
print(f"串行耗时：{time.time() - start:.1f} 秒")
```

并行版本约为串行版本耗时的 **1/3**（如果三个 LLM 调用耗时相近）。

---

## 6. 实验 4：条件分支链

### 6.1 目标

根据告警的严重程度，选择不同的处理流程。

### 6.2 场景

运维平台收到告警后自动判断：
- **critical 级别**：立即呼叫值班专家
- **warning 级别**：自动分析并给出建议
- **info 级别**：只记录日志

### 6.3 定义三条处理链

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def make_response_chain(role_instruction):
    prompt = ChatPromptTemplate.from_messages([
        ("system", role_instruction),
        ("human", "告警内容：{alert_description}\n实例：{instance}"),
    ])
    return prompt | llm | StrOutputParser()

critical_chain = make_response_chain(
    "你是一位高级值班专家。告警非常紧急，请立即给出需要执行的命令和联系人。"
)

warning_chain = make_response_chain(
    "你是一位运维分析工程师。请分析告警原因并给出排查步骤。"
)

info_chain = make_response_chain(
    "你是一位运维记录员。用一句话记录这条告警信息。"
)
```

### 6.4 组合成条件分支

```python
from langchain_core.runnables import RunnableBranch

# 先写一个判别函数：从原始输入中取出 severity 并判断
def severity_is(level: str):
    """返回一个判断函数"""
    return lambda x: x.get("severity") == level

branch = RunnableBranch(
    (severity_is("critical"), critical_chain),
    (severity_is("warning"), warning_chain),
    # 默认走 info 链
    info_chain,
)
```

### 6.5 分别测试三种场景

```python
# critical 告警
result = branch.invoke({
    "severity": "critical",
    "alert_description": "核心数据库宕机，所有业务不可用",
    "instance": "db-prod-01",
})
print("【critical 响应】\n", result)
print()

# warning 告警
result = branch.invoke({
    "severity": "warning",
    "alert_description": "应用服务器内存使用率超过 85%",
    "instance": "app-prod-03",
})
print("【warning 响应】\n", result)
print()

# info 告警
result = branch.invoke({
    "severity": "info",
    "alert_description": "每日备份任务完成",
    "instance": "backup-scheduler",
})
print("【info 响应】\n", result)
```

### 6.6 理解条件分发

```
{"severity": "critical", ...}
              │
              ▼
     severity == "critical"？
        │           │
       是            否
        │            │
        ▼            ▼
  critical_chain   severity == "warning"？
                       │           │
                      是            否
                       │            │
                       ▼            ▼
                 warning_chain   info_chain（默认）
```

`RunnableBranch` 按顺序检查条件，第一个匹配的会被执行，后面的不再检查。最后一个可以不写条件，作为 **默认分支**。

---

## 7. 综合实验 5：自定义函数的插入

### 7.1 目标

在 LCEL 链中插入 Python 函数，处理模型输出后的清洗/转换。

### 7.2 场景

模型对 AIOps 诊断输出的字符串中可能有多余的换行和 Markdown 标记，需要在返回前清洗。

### 7.3 代码

```python
import re
from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. 清洗函数
def clean_diagnosis(text: str) -> str:
    """去掉多余的 Markdown 标记和空行"""
    # 去掉 Markdown 代码块标记
    text = re.sub(r'```\w*\n?', '', text)
    # 合并多个连续空行为一个
    text = re.sub(r'\n{3,}', '\n\n', text)
    # 去掉首尾空白
    return text.strip()

# 2. 构建带清洗的链
prompt = PromptTemplate.from_template(
    "请为以下运维问题给出诊断：{problem}"
)

chain = prompt | llm | StrOutputParser() | RunnableLambda(clean_diagnosis)

# 3. 测试
result = chain.invoke({
    "problem": "Redis 内存使用率突然从 40% 飙升到 95%，可能的原因是什么？"
})
print(result)
```

注意这条链的结构：

```
prompt → llm → StrOutputParser → clean_diagnosis
```

`RunnableLambda` 让任何 Python 函数都能嵌入链中，这是 LCEL 强大的地方。

---

## 8. 实验 6：RunnablePassthrough 透传

### 8.1 目标

在链中透传部分输入，同时附加 LLM 生成的新字段。

### 8.2 场景

用户输入告警信息，链不仅要返回诊断，还要在结果中保留原始告警的 `alert_id` 和 `timestamp`，方便下游持久化。

### 8.3 代码

```python
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 诊断子链（只处理告警描述）
diag_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一位运维专家。请对以下告警给出诊断。"),
    ("human", "{alert_description}"),
])
diag_chain = diag_prompt | llm | StrOutputParser()

# 组合：保留原始字段 + 附加诊断结果
full_chain = RunnablePassthrough.assign(
    diagnosis=lambda x: diag_chain.invoke({"alert_description": x["alert_description"]})
)

# 运行
result = full_chain.invoke({
    "alert_id": "ALT-2026-0001",
    "timestamp": "2026-06-30T14:30:00Z",
    "alert_description": "web-server-01 Nginx 返回大量 502 错误",
})

print("alert_id:", result["alert_id"])          # 原始字段被保留
print("timestamp:", result["timestamp"])        # 原始字段被保留
print("diagnosis:", result["diagnosis"][:200])  # 新增的诊断结果
```

---

## 9. 课后作业

### 必做作业

1. **搭建 5 条链**：
   - 用 `ChatPromptTemplate + ChatOpenAI + StrOutputParser` 实现一个 "技术翻译" 链（把中文技术术语翻译成英文，并附带解释）
   - 用 `PydanticOutputParser` 实现一个 "服务器配置审计" 链（输入配置项，输出审计结果，包含合规性和风险等级）
   - 用 `RunnableParallel` 实现一个 "代码审查" 链（同时做安全检查、性能分析、可读性打分）
   - 用 `RunnableBranch` 实现一个 "问题分级" 链（根据问题类型选择不同的回答策略）
   - 用 `RunnableLambda` 给某条链的最终输出加上时间戳和编号

2. **对比实验**：
   - 用同一个问题分别调用 `chain.invoke()` 和 `chain.stream()`，记录输出体验的区别。
   - 用 `batch` 一次处理 5 条问题，与分别 `invoke` 5 次对比耗时。

3. **代码整理**：
   - 把实验 1-6 的代码整理成一个 `.py` 文件，每段代码加上注释说明其作用。

### 选做作业

1. **链的图结构可视化**：给实验 5 的链调用 `chain.get_graph().print_ascii()`，把输出截图保存。

2. **RunnablePassthrough 高级用法**：在实验 6 的基础上，让诊断链也返回 `token_usage` 元信息。

3. **对接项目接口**：用 FastAPI 把实验 2 的 `AlertDiagnosis` 链包装成 API 接口：
   ```python
   @app.post("/api/diagnose")
   async def diagnose(alert: AlertRequest) -> AlertDiagnosis:
       result = await chain.ainvoke({...})
       return result
   ```

---

## 10. 常见问题

### Q1：LLM 调用报 401 / 403

**原因**：API Key 未设置或已过期。

**解决**：
```bash
echo $DASHSCOPE_API_KEY
```
如果为空，检查 `.env` 文件是否存在，`python-dotenv` 是否已安装。

### Q2：PydanticOutputParser 报 "Failed to parse"

**原因**：模型没有输出纯 JSON，或 JSON 结构不符合模型定义。

**解决**：
- 检查 prompt 中是否包含 `format_instructions`
- 尝试用更强的模型（`qwen-max` 比 `qwen-turbo` 遵守格式能力更强）
- 在 prompt 中加一句 "请严格只输出 JSON，不要输出其他内容"

### Q3：并行链的结果顺序和输入顺序不一致

**原因**：`RunnableParallel` 的结果是字典，字典在 Python 3.7+ 保持插入顺序（即你定义分支的顺序），与执行顺序无关。

**解决**：这是正常行为。如果你需要对结果排序，在链外用代码处理。

### Q4：RunnableBranch 的所有条件都是 False

**原因**：最后的默认分支没有生效。

**解决**：确保 `RunnableBranch` 的最后一个参数是默认链（不带条件判断的函数）。

### Q5：链运行很慢

**原因**：可能是 LLM 响应慢，或链里有同步阻塞调用。

**解决**：
- 使用 `qwen-turbo` 代替 `qwen-max`（更快）
- 在 FastAPI 中用 `ainvoke` 代替 `invoke`
- 用 `RunnableParallel` 并行化独立调用

---

## 11. 第 6 课整体总结

经过三节课的系统学习，你已经掌握了 LangChain 最核心的基础知识：

| 知识模块 | 具体内容 |
|---------|---------|
| **LangChain 定位** | LLM 应用开发框架，解决直接调 API 的痛点 |
| **版本分层** | `langchain-core` / `langchain` / partner packages 的分工 |
| **Model I/O** | `ChatOpenAI`、`ChatPromptTemplate`、`StrOutputParser`、`PydanticOutputParser` |
| **Chain** | LCEL 管道语法 `prompt \| llm \| parser` |
| **运行方式** | `invoke`、`ainvoke`、`stream`、`astream`、`batch`、`abatch` |
| **Runnable 组件** | `RunnableLambda`、`RunnablePassthrough`、`RunnableParallel`、`RunnableBranch` |
| **动手实验** | 6 个完整实验，覆盖基础链、结构化输出、并行、分支、自定义函数、透传 |

### 能力检验

学完第 6 课，你应该能独立完成：

- ✅ 创建一个 ChatOpenAI 实例连接 DashScope
- ✅ 编写带角色的 ChatPromptTemplate
- ✅ 用 PydanticOutputParser 把 LLM 输出转成结构化数据
- ✅ 用 `|` 管道符把 Prompt、Model、Parser 串成链
- ✅ 用 `invoke` / `stream` / `batch` 运行链
- ✅ 在链中插入自定义 Python 函数
- ✅ 搭建并行分支和条件分支链
- ✅ 调试和排查链的常见错误

### 下节课预告

**第 7 课：LLM 工厂与 OpenAI 兼容模式**

我们将进入项目实战，学习：

- 阿里云 DashScope OpenAI 兼容接口的完整配置
- `langchain_openai.ChatOpenAI` 的进阶参数
- 工厂模式封装 LLM（`app/core/llm_factory.py`）
- 如何在一个项目里同时管理多个模型（`qwen-max`、`qwen-turbo`）
- 模型切换的最佳实践

---

## 12. 参考资料

- [LangChain Expression Language (LCEL) 完整文档](https://python.langchain.com/docs/concepts/lcel/)
- [LangChain Runnables](https://python.langchain.com/docs/concepts/runnables/)
- [LangChain Output Parsers](https://python.langchain.com/docs/concepts/output_parsers/)
- [LangChain OpenAI 集成](https://python.langchain.com/docs/integrations/chat/openai/)
- [阿里云 DashScope 开发文档](https://help.aliyun.com/zh/dashscope/)

---

*生成时间：2026/06/30*  
*课程：AIAgent 项目实战 · 第 6 课（三）*
