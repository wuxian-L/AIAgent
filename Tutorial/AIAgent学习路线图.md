# AIAgent 项目学习路线图

> 基于 `AgentProject/super_biz_agent_py-release-2026-05-17` 的企业级 AIOps Agent 项目整理。
> 目标：通过本项目系统学习 Agent 搭建、LangChain、RAG、MCP 等核心技术。

---

## 一、项目全局认知

`super_biz_agent_py` 是一个**企业级智能对话和运维助手**，核心能力分为两块：

| 能力 | 技术实现 | 对应文件 |
|------|---------|---------|
| **RAG 知识库问答** | LangGraph 状态图 + ChatQwen + 知识检索工具 | `app/services/rag_agent_service.py` |
| **AIOps 智能诊断** | Plan-Execute-Replan 工作流 | `app/services/aiops_service.py` + `app/agent/aiops/` |
| **工具调用** | MCP 协议接入日志/监控工具 | `mcp_servers/cls_server.py`、`monitor_server.py` |
| **向量检索** | Milvus + DashScope Embedding | `app/services/vector_store_manager.py` |
| **Web 服务** | FastAPI + 静态页面 | `app/main.py`、`static/` |

**技术栈：**
- 框架：FastAPI + LangChain + LangGraph
- LLM：阿里云 DashScope（通义千问）
- 向量库：Milvus
- 工具协议：MCP（Model Context Protocol）
- 部署：Docker + uv

**学习原则：** 先跑通项目，再分层拆解，不要一开始逐行精读。

---

## 二、循序渐进的学习路线

### 第一阶段：把项目跑起来（1~2 天）

目标：建立信心，理解各组件如何协作。

#### 1.1 环境准备

```powershell
# 1. 进入项目目录
cd AgentProject/super_biz_agent_py-release-2026-05-17

# 2. 创建虚拟环境并安装依赖
pip install uv
uv venv
.venv\Scripts\activate
uv pip install -e .

# 3. 编辑 .env 文件，填入 DASHSCOPE_API_KEY
notepad .env

# 4. 启动 Milvus 向量数据库（需 Docker Desktop）
docker compose -f vector-database.yml up -d

# 5. 启动 MCP 服务（两个独立窗口）
python mcp_servers/cls_server.py
python mcp_servers/monitor_server.py

# 6. 启动 FastAPI 主服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 9900

# 7. 上传文档到向量库
python -c "import requests, os, time; [requests.post('http://localhost:9900/api/upload', files={'file': open(f'aiops-docs/{f}', 'rb')}) or time.sleep(1) for f in os.listdir('aiops-docs') if f.endswith('.md')]"
```

Windows 也可以直接使用：
```powershell
.\start-windows.bat    # 启动所有服务
.\stop-windows.bat     # 停止所有服务
```

#### 1.2 体验接口

- Web 界面：`http://localhost:9900`
- API 文档：`http://localhost:9900/docs`
- 测试接口：
  - `POST /api/chat`：普通对话
  - `POST /api/chat_stream`：流式对话
  - `POST /api/aiops`：AIOps 诊断

#### 1.3 重点阅读文件

| 文件 | 学习重点 |
|------|---------|
| `README.md` | 项目全景、启动流程、接口说明 |
| `app/main.py` | FastAPI 入口、路由注册、生命周期、CORS、静态文件 |
| `app/config.py` | Pydantic Settings 配置管理、环境变量 |

#### 1.4 学习要点

理解主链路：
```
用户请求 → API 路由 → Service 服务 → LLM / 工具 → 返回结果
```

不要纠结 LangGraph 细节，先建立整体感知。

---

### 第二阶段：理解 RAG 知识库问答（2~3 天）

这是项目里最完整、最适合入门的 Agent 实现。

#### 2.1 文档处理与向量化

| 文件 | 学习重点 |
|------|---------|
| `app/services/document_splitter_service.py` | Markdown 文档切分策略、标题提取、chunk 大小 |
| `app/services/vector_embedding_service.py` | DashScope Embedding 模型封装 |
| `app/services/vector_store_manager.py` | Milvus VectorStore 初始化、文档增删、相似度检索 |
| `app/services/vector_index_service.py` | 上传文档时建立索引的流程 |
| `app/services/vector_search_service.py` | 向量搜索服务封装 |

#### 2.2 知识检索工具

| 文件 | 学习重点 |
|------|---------|
| `app/tools/knowledge_tool.py` | `@tool` 装饰器、`retrieve_knowledge`、文档格式化 |

注意 `@tool(response_format="content_and_artifact")` 的用法，它同时返回给 LLM 的上下文和原始文档。

#### 2.3 RAG Agent 核心

精读 `app/services/rag_agent_service.py`：

- `AgentState`：状态定义
- `MemorySaver`：会话记忆持久化
- `ChatQwen`：阿里千问模型原生集成
- `create_agent`：绑定 LLM + Tools
- `query` / `query_stream`：非流式与流式输出
- `trim_messages_middleware`：消息历史修剪策略
- `get_session_history` / `clear_session`：会话管理

#### 2.4 动手实验

1. 修改 `.env` 中的 `CHUNK_MAX_SIZE` 和 `CHUNK_OVERLAP`，观察回答效果变化。
2. 在 `aiops-docs/` 目录添加自己的 Markdown 文档，重新上传，测试问答。
3. 修改 `RAG_TOP_K`（3 → 5 → 1），观察召回数量和质量。
4. 在 `rag_agent_service.py` 中修改系统提示词，观察回答风格变化。

#### 2.5 配套学习

- [LangChain RAG 教程](https://python.langchain.com/docs/tutorials/rag/)
- [LangChain Build an Agent](https://python.langchain.com/docs/tutorials/agents/)
- [阿里千问 LangChain 集成](https://docs.langchain.com/oss/python/integrations/chat/qwen)

---

### 第三阶段：掌握 Agent 工具与 MCP 协议（2~3 天）

这是项目最有特色的部分，学习如何给 Agent 接入外部能力。

#### 3.1 本地工具

| 文件 | 学习重点 |
|------|---------|
| `app/tools/__init__.py` | 工具注册、默认工具列表 |
| `app/tools/time_tool.py` | 最简单的工具示例 |
| `app/tools/knowledge_tool.py` | 带返回值的复杂工具 |

#### 3.2 MCP 服务器

| 文件 | 学习重点 |
|------|---------|
| `mcp_servers/README.md` | MCP 服务说明、工具列表 |
| `mcp_servers/cls_server.py` | CLS 日志查询服务（端口 8003） |
| `mcp_servers/monitor_server.py` | 监控数据服务（端口 8004） |

学习 FastMCP 如何暴露工具，以及模拟数据与真实 API 的接入点。

#### 3.3 MCP 客户端

精读 `app/agent/mcp_client.py`：

- `MultiServerMCPClient`：多服务器管理
- 单例模式：避免重复初始化
- `retry_interceptor`：工具调用重试拦截器（指数退避）
- `load_mcp_tools_safe`：安全加载工具
- `suggest_mcp_transport`：transport 与 URL 匹配建议

#### 3.4 动手实验

1. 在 `mcp_servers/monitor_server.py` 中新增一个工具，例如 `query_disk_metrics`。
2. 重启 MCP 服务，测试 RAG Agent 是否能自动调用新工具。
3. 修改 `retry_interceptor` 的最大重试次数，观察失败处理。
4. 尝试把 `mcp_cls_url` 或 `mcp_monitor_url` 改错，观察错误处理。

#### 3.5 配套学习

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters)
- [FastMCP 文档](https://github.com/jlowin/fastmcp)

---

### 第四阶段：攻克 AIOps 智能诊断（3~5 天）

这是项目最复杂的部分，涉及 **Plan-Execute-Replan** 模式。

#### 4.1 工作流编排

精读 `app/services/aiops_service.py`：

- `StateGraph` 构建：Planner → Executor → Replanner
- `should_continue`：条件边，控制流程继续或结束
- `execute` / `diagnose`：通用执行与 AIOps 诊断接口
- 事件格式化：`_format_planner_event`、`_format_executor_event`、`_format_replanner_event`

#### 4.2 三个核心节点

| 文件 | 职责 | 学习重点 |
|------|------|---------|
| `app/agent/aiops/planner.py` | 制定诊断计划 | 如何生成 4-6 个步骤 |
| `app/agent/aiops/executor.py` | 执行单步 | 如何调用工具、记录结果 |
| `app/agent/aiops/replanner.py` | 重新规划 | 如何评估结果、决定继续或终止 |
| `app/agent/aiops/state.py` | 状态定义 | `PlanExecuteState` 字段含义 |
| `app/agent/aiops/utils.py` | 工具函数 | 辅助方法 |

#### 4.3 提示工程

重点阅读 `app/services/aiops_service.py` 中 `diagnose()` 方法里的报告格式 Prompt：

- 为什么输出格式定义得如此详细？
- 如何要求模型基于真实数据、禁止编造？
- Markdown 表格和结构化输出的 Prompt 技巧

#### 4.4 动手实验

1. 修改 Planner 的 Prompt，让诊断步骤从 4~6 步变成 2~3 步。
2. 给 AIOps 增加一个新的 MCP 工具调用。
3. 修改报告模板，输出你需要的字段。
4. 在 `diagnose()` 中修改任务描述，让它诊断指定的服务而非全系统。

#### 4.5 配套学习

- [LangGraph Plan-Execute 官方教程](https://langchain-ai.github.io/langgraph/tutorials/plan-and-execute/)

---

### 第五阶段：工程化与扩展（长期）

当你能看懂并修改核心代码后，可以往这些方向深入：

| 方向 | 项目切入点 | 建议实践 |
|------|----------|---------|
| **Prompt 工程** | `rag_agent_service.py` 系统提示、`aiops_service.py` 报告模板 | 尝试 few-shot、CoT、角色设定 |
| **记忆优化** | `MemorySaver`、`trim_messages_middleware` | 按 token 数修剪、接入 Redis/Postgres 持久化 |
| **多模型切换** | `app/core/llm_factory.py` | RAG 用小模型、AIOps 用大模型 |
| **评估与测试** | `pyproject.toml` 中的 pytest 配置 | 给 RAG 加召回率测试、给 AIOps 加流程测试 |
| **真实工具接入** | `mcp_servers/` | 把 mock 数据换成真实 CLS/Prometheus API |
| **前端联动** | `static/app.js` | 看懂 SSE 流式输出如何渲染 |
| **日志与可观测性** | `app/utils/logger.py` | 学习 Loguru 配置、日志轮转 |

---

## 三、推荐学习顺序

```
第 1 天：跑通项目
  → 读 README.md
  → 读 app/main.py
  → 读 app/config.py
  → 体验 /api/chat、/api/chat_stream、/api/aiops

第 2-3 天：RAG 流程
  → app/services/document_splitter_service.py
  → app/services/vector_embedding_service.py
  → app/services/vector_store_manager.py
  → app/services/vector_index_service.py
  → app/tools/knowledge_tool.py
  → app/services/rag_agent_service.py

第 4-5 天：工具与 MCP
  → app/tools/__init__.py
  → app/tools/time_tool.py
  → mcp_servers/cls_server.py
  → mcp_servers/monitor_server.py
  → app/agent/mcp_client.py

第 6-8 天：AIOps 诊断
  → app/services/aiops_service.py
  → app/agent/aiops/state.py
  → app/agent/aiops/planner.py
  → app/agent/aiops/executor.py
  → app/agent/aiops/replanner.py

第 9 天起：扩展改造
  → 新增工具 / 修改 Prompt / 接真实 API / 写测试
```

---

## 四、针对性学习建议

1. **不要跳过 Milvus 和 Docker**
   RAG 的核心是向量检索，理解 Milvus 的 collection、embedding、similarity search 非常重要。

2. **重点关注“状态”和“图”**
   LangGraph 的精髓是 `State` + `Graph`。理解了 `AgentState` 和 `PlanExecuteState`，就理解了项目 70% 的 Agent 逻辑。

3. **多打日志、多改配置**
   项目使用 `loguru`，日志清晰。打开 `debug` 模式，观察 LLM 的 tool call 过程，比看文档更直观。

4. **从修改开始，而不是重写**
   先小改：加一个工具、改一个 Prompt、调一个参数。能预测改动效果后，再考虑自己搭一个 Agent。

5. **边读边画流程图**
   尤其是 AIOps 的 Plan-Execute-Replan 流程，建议边读代码边画状态流转图。

6. **记录问题和心得**
   每读完一个模块，记录：这个模块解决了什么问题？如果我自己做会怎么设计？这个项目的设计取舍是什么？

---

## 五、核心文件速查表

| 文件 | 所属模块 | 作用 |
|------|---------|------|
| `app/main.py` | 入口 | FastAPI 应用入口 |
| `app/config.py` | 配置 | 环境变量与配置管理 |
| `app/core/llm_factory.py` | 核心 | LLM 工厂（OpenAI 兼容模式） |
| `app/core/milvus_client.py` | 核心 | Milvus 连接管理 |
| `app/api/chat.py` | API | 对话接口 |
| `app/api/aiops.py` | API | AIOps 接口 |
| `app/api/file.py` | API | 文件上传接口 |
| `app/services/rag_agent_service.py` | 服务 | RAG Agent 核心 |
| `app/services/aiops_service.py` | 服务 | AIOps Plan-Execute-Replan |
| `app/services/vector_store_manager.py` | 服务 | 向量存储管理 |
| `app/services/vector_embedding_service.py` | 服务 | Embedding 服务 |
| `app/services/document_splitter_service.py` | 服务 | 文档切分 |
| `app/tools/knowledge_tool.py` | 工具 | 知识检索工具 |
| `app/tools/time_tool.py` | 工具 | 时间工具 |
| `app/agent/mcp_client.py` | Agent | MCP 客户端管理 |
| `app/agent/aiops/planner.py` | Agent | 诊断计划制定 |
| `app/agent/aiops/executor.py` | Agent | 步骤执行 |
| `app/agent/aiops/replanner.py` | Agent | 重新规划 |
| `app/agent/aiops/state.py` | Agent | 状态定义 |
| `mcp_servers/cls_server.py` | MCP | 日志查询服务 |
| `mcp_servers/monitor_server.py` | MCP | 监控数据服务 |
| `static/app.js` | 前端 | Web 界面逻辑 |

---

*生成时间：2026/06/26*
