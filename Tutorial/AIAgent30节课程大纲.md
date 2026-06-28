# AIAgent 项目实战课程大纲（30 节课）

> 基于 `AgentProject/super_biz_agent_py-release-2026-05-17` 项目设计
> 目标：系统掌握 Agent 搭建、LangChain、RAG、MCP、AIOps 等企业级技术

---

## 课程说明

- **总课时**：30 节
- **每节时长**：建议 45-90 分钟（理论 + 实操）
- **前置要求**：Python 基础、了解 HTTP/API 基本概念
- **学习顺序**：按模块递进，建议不要跳课

---

## 模块一：项目概览与环境搭建（第 1-3 课）

### 第 1 课：项目全景与技术架构
- **目标**：理解项目定位、核心能力、技术栈
- **内容**：
  - 什么是企业级 AIOps Agent
  - RAG 知识库问答 vs AIOps 智能诊断
  - 技术栈总览：FastAPI + LangChain + LangGraph + Milvus + MCP + DashScope
  - 项目目录结构解读
- **对应文件**：`README.md`
- **实践作业**：画出项目架构图，标注每个组件的作用

### 第 2 课：开发环境搭建
- **目标**：成功运行项目
- **内容**：
  - Python 3.11+ 与虚拟环境
  - `uv` 包管理器使用
  - `.env` 配置文件
  - Docker Desktop 与 Milvus 启动
- **对应文件**：`.env`、`pyproject.toml`、`vector-database.yml`
- **实践作业**：独立完成环境搭建，启动 Milvus 服务

### 第 3 课：服务启动与接口体验
- **目标**：跑通完整流程，体验 Agent 能力
- **内容**：
  - 启动 MCP 服务（CLS / Monitor）
  - 启动 FastAPI 主服务
  - 上传文档到向量库
  - 体验 Web 界面与 API 文档
- **对应文件**：`start-windows.bat`、`app/main.py`
- **实践作业**：用 curl 测试 `/api/chat`、`/api/chat_stream`、`/api/aiops`

---

## 模块二：FastAPI 与项目骨架（第 4-5 课）

### 第 4 课：FastAPI 应用入口
- **目标**：掌握 FastAPI 生命周期、路由、中间件
- **内容**：
  - `FastAPI()` 应用创建
  - `@asynccontextmanager` 生命周期管理
  - CORS 中间件配置
  - 静态文件挂载
- **对应文件**：`app/main.py`
- **实践作业**：在 `app/main.py` 中新增一个 `/api/hello` 测试接口

### 第 5 课：配置管理与数据模型
- **目标**：掌握 Pydantic Settings 和数据模型设计
- **内容**：
  - `pydantic-settings` 环境变量管理
  - `BaseSettings` 配置类
  - Pydantic 模型：`request.py`、`response.py`、`aiops.py`、`document.py`
- **对应文件**：`app/config.py`、`app/models/*.py`
- **实践作业**：在 `.env` 中新增一个自定义配置项，并在 `config.py` 中读取

---

## 模块三：LangChain 基础与 LLM 集成（第 6-9 课）

### 第 6 课：LangChain 核心概念
- **目标**：理解 LangChain 的核心抽象
- **内容**：
  - Model / Prompt / Output Parser
  - Chain 的构建与运行
  - LCEL（LangChain Expression Language）入门
- **对应文件**：`pyproject.toml` 依赖说明
- **实践作业**：独立写一个最简单的 `PromptTemplate → LLM → StrOutputParser` Chain

### 第 7 课：LLM 工厂与 OpenAI 兼容模式
- **目标**：学会集成不同 LLM 提供商
- **内容**：
  - 阿里云 DashScope OpenAI 兼容接口
  - `langchain_openai.ChatOpenAI`
  - 工厂模式封装 LLM
- **对应文件**：`app/core/llm_factory.py`
- **实践作业**：用 `LLMFactory` 分别调用 `qwen-max` 和 `qwen-turbo`

### 第 8 课：ChatQwen 原生集成
- **目标**：理解项目为什么使用 ChatQwen
- **内容**：
  - `langchain_qwq.ChatQwen`
  - 流式输出配置
  - 原生集成 vs OpenAI 兼容模式的取舍
- **对应文件**：`app/services/rag_agent_service.py`（初始化部分）
- **实践作业**：对比 `ChatOpenAI` 和 `ChatQwen` 的流式输出差异

### 第 9 课：消息模型与会话管理
- **目标**：掌握 LangChain 消息类型
- **内容**：
  - `SystemMessage`、`HumanMessage`、`AIMessage`
  - 消息历史的维护
  - 上下文窗口与消息修剪
- **对应文件**：`app/services/rag_agent_service.py` 中 `trim_messages_middleware`
- **实践作业**：实现一个按 token 数修剪消息历史的函数

---

## 模块四：RAG 知识库构建（第 10-15 课）

### 第 10 课：RAG 原理与流程
- **目标**：理解 RAG 完整流程
- **内容**：
  - 检索增强生成的概念
  - 文档 → 分块 → Embedding → 向量库 → 检索 → 生成
  - RAG 能解决什么问题
- **对应文件**：`README.md` 中 RAG 相关说明
- **实践作业**：画出 RAG 数据流图

### 第 11 课：文档加载与切分
- **目标**：掌握文档切分策略
- **内容**：
  - Markdown 文档处理
  - `RecursiveCharacterTextSplitter`
  - 标题提取与元数据保留
  - chunk size / overlap 的影响
- **对应文件**：`app/services/document_splitter_service.py`
- **实践作业**：用不同 `CHUNK_MAX_SIZE` 切分同一篇文档，对比结果

### 第 12 课：Embedding 与向量化
- **目标**：理解 Embedding 服务如何工作
- **内容**：
  - `text-embedding-v4` 模型
  - `DashScopeEmbeddings` 封装
  - 批量向量化
- **对应文件**：`app/services/vector_embedding_service.py`
- **实践作业**：手写一段代码，将句子列表转为向量

### 第 13 课：Milvus 向量数据库
- **目标**：掌握 Milvus 基础操作
- **内容**：
  - Milvus collection、field、index 概念
  - `langchain_milvus.Milvus` 集成
  - 连接管理
- **对应文件**：`app/core/milvus_client.py`、`app/services/vector_store_manager.py`
- **实践作业**：用 Python 代码查询 Milvus collection 的 schema

### 第 14 课：向量存储管理器
- **目标**：掌握文档增删查流程
- **内容**：
  - `VectorStoreManager` 初始化
  - `add_documents` 批量添加
  - `delete_by_source` 按来源删除
  - `similarity_search` 相似度检索
- **对应文件**：`app/services/vector_store_manager.py`
- **实践作业**：实现一个按文件名更新知识库的功能

### 第 15 课：文件上传与索引接口
- **目标**：打通文档上传 → 切分 → 入库流程
- **内容**：
  - FastAPI 文件上传
  - 文档索引服务
  - 重复上传时更新旧数据
- **对应文件**：`app/api/file.py`、`app/services/vector_index_service.py`
- **实践作业**：写一个脚本批量上传 `aiops-docs/` 目录下所有文档

---

## 模块五：Agent 与工具调用（第 16-20 课）

### 第 16 课：LangChain Agent 基础
- **目标**：理解 Agent 的工作原理
- **内容**：
  - Agent 与 Chain 的区别
  - ReAct 模式简介
  - `create_agent` 与工具绑定
- **对应文件**：`app/services/rag_agent_service.py`
- **实践作业**：用 `create_agent` + 一个简单工具实现加法 Agent

### 第 17 课：本地工具开发
- **目标**：学会编写和注册工具
- **内容**：
  - `@tool` 装饰器
  - 工具参数与返回值
  - `response_format="content_and_artifact"`
- **对应文件**：`app/tools/time_tool.py`、`app/tools/knowledge_tool.py`
- **实践作业**：新增一个 `get_weather` 工具（返回 mock 数据）

### 第 18 课：LangGraph 状态图基础
- **目标**：掌握 LangGraph 核心概念
- **内容**：
  - `StateGraph`
  - Node 与 Edge
  - `add_messages` 与状态注解
  - `MemorySaver` 检查点
- **对应文件**：`app/services/rag_agent_service.py` 中 `AgentState`
- **实践作业**：独立实现一个“打招呼 → 反问 → 结束”的三节点 LangGraph

### 第 19 课：MCP 协议与 FastMCP 服务器
- **目标**：理解 MCP 协议和服务器实现
- **内容**：
  - Model Context Protocol 协议概念
  - FastMCP 框架
  - 如何暴露工具给外部 Agent
- **对应文件**：`mcp_servers/cls_server.py`、`mcp_servers/monitor_server.py`
- **实践作业**：在 `monitor_server.py` 新增 `query_disk_metrics` 工具

### 第 20 课：MCP 客户端与工具集成
- **目标**：掌握多 MCP 服务器管理和工具加载
- **内容**：
  - `MultiServerMCPClient`
  - 单例模式与延迟初始化
  - 重试拦截器
  - transport 配置（stdio / sse / streamable-http）
- **对应文件**：`app/agent/mcp_client.py`
- **实践作业**：故意配置错误的 MCP URL，观察重试与降级行为

---

## 模块六：AIOps 智能诊断（第 21-25 课）

### 第 21 课：AIOps 场景与 Plan-Execute-Replan 模式
- **目标**：理解 AIOps 诊断场景和设计模式
- **内容**：
  - 什么是 AIOps
  - Plan-Execute-Replan 设计模式
  - 与传统 Agent 的区别
- **对应文件**：`README.md` 中 AIOps 部分
- **实践作业**：用自己的话解释 Plan-Execute-Replan 的工作流程

### 第 22 课：状态定义与图构建
- **目标**：掌握 AIOps 工作流的状态和图
- **内容**：
  - `PlanExecuteState` 状态字段
  - `StateGraph` 构建
  - 条件边 `should_continue`
- **对应文件**：`app/services/aiops_service.py`、`app/agent/aiops/state.py`
- **实践作业**：画出 AIOps 状态流转图

### 第 23 课：Planner 计划制定
- **目标**：理解诊断计划如何生成
- **内容**：
  - Planner 的 Prompt 设计
  - 如何生成可执行的步骤列表
  - 计划的结构化输出
- **对应文件**：`app/agent/aiops/planner.py`
- **实践作业**：修改 Planner Prompt，让计划步骤数可变

### 第 24 课：Executor 步骤执行
- **目标**：理解单步执行和工具调用
- **内容**：
  - 从 plan 中取下一步
  - 调用工具并记录结果
  - `past_steps` 状态更新
- **对应文件**：`app/agent/aiops/executor.py`
- **实践作业**：给 Executor 增加执行耗时记录

### 第 25 课：Replanner 重新规划
- **目标**：理解动态调整与终止判断
- **内容**：
  - 评估执行结果
  - 决定继续执行、重新规划、生成报告
  - 最终响应的生成
- **对应文件**：`app/agent/aiops/replanner.py`
- **实践作业**：调整 Replanner 的终止条件，观察诊断流程变化

---

## 模块七：工程化与扩展（第 26-30 课）

### 第 26 课：日志与可观测性
- **目标**：掌握项目日志体系
- **内容**：
  - Loguru 配置
  - 日志轮转与文件输出
  - 不同模块的日志级别控制
- **对应文件**：`app/utils/logger.py`
- **实践作业**：为 AIOps 流程增加更详细的步骤日志

### 第 27 课：流式输出与前端交互
- **目标**：理解 SSE 流式输出
- **内容**：
  - Server-Sent Events (SSE)
  - `stream_mode="messages"` vs `"updates"`
  - 前端如何接收和渲染流式数据
- **对应文件**：`app/api/chat.py`、`app/api/aiops.py`、`static/app.js`
- **实践作业**：修改前端，让流式输出显示当前执行节点名称

### 第 28 课：会话管理与持久化
- **目标**：掌握会话状态管理
- **内容**：
  - `thread_id` 与会话隔离
  - `MemorySaver` 的 get/delete
  - 会话历史查询与清空
- **对应文件**：`app/services/rag_agent_service.py` 中会话相关方法
- **实践作业**：实现一个查看所有活跃会话的接口

### 第 29 课：测试与评估
- **目标**：为 Agent 项目编写测试
- **内容**：
  - pytest 与 pytest-asyncio
  - 单元测试 vs 集成测试
  - RAG 召回率评估思路
  - AIOps 流程测试
- **对应文件**：`pyproject.toml` 中 pytest 配置
- **实践作业**：为 `knowledge_tool.py` 写一个单元测试

### 第 30 课：真实场景改造与项目总结
- **目标**：将项目改造为真实可用系统
- **内容**：
  - 接入真实 CLS / Prometheus API
  - 多模型路由策略
  - 生产环境部署考虑
  - 项目学习回顾与知识地图
- **对应文件**：`mcp_servers/README.md`
- **实践作业**：选择一个方向完成改造：接入真实 API / 增加新工具 / 优化 Prompt / 持久化会话

---

## 附录：学习资源

### 官方文档
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [LangChain 文档](https://python.langchain.com/)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [LangGraph Plan-Execute](https://langchain-ai.github.io/langgraph/tutorials/plan-and-execute/)
- [MCP 协议](https://modelcontextprotocol.io/)
- [阿里云 DashScope](https://dashscope.aliyun.com/)

### 项目核心文件速查

| 文件 | 课程覆盖 |
|------|---------|
| `README.md` | 第 1 课 |
| `app/main.py` | 第 4 课 |
| `app/config.py` | 第 5 课 |
| `app/core/llm_factory.py` | 第 7 课 |
| `app/core/milvus_client.py` | 第 13 课 |
| `app/services/rag_agent_service.py` | 第 8、9、16、18、28 课 |
| `app/services/aiops_service.py` | 第 21、22 课 |
| `app/services/vector_store_manager.py` | 第 14 课 |
| `app/services/document_splitter_service.py` | 第 11 课 |
| `app/services/vector_embedding_service.py` | 第 12 课 |
| `app/tools/knowledge_tool.py` | 第 17 课 |
| `app/tools/time_tool.py` | 第 17 课 |
| `app/agent/mcp_client.py` | 第 20 课 |
| `app/agent/aiops/planner.py` | 第 23 课 |
| `app/agent/aiops/executor.py` | 第 24 课 |
| `app/agent/aiops/replanner.py` | 第 25 课 |
| `mcp_servers/cls_server.py` | 第 19 课 |
| `mcp_servers/monitor_server.py` | 第 19 课 |
| `static/app.js` | 第 27 课 |

---

*生成时间：2026/06/26*
