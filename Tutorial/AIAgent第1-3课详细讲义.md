# AIAgent 项目实战课程 · 第 1-3 课详细讲义

> 课程基于 `AgentProject/super_biz_agent_py-release-2026-05-17` 项目
> 学习方式：理论 + 代码解读 + 动手实验

---

# 第 1 课：项目全景与技术架构

## 1.1 本课目标

通过本课学习，你能够：
- 说清楚这个项目是做什么的
- 理解 RAG 问答与 AIOps 诊断两大核心能力
- 熟悉项目使用的技术栈
- 能够画出项目的整体架构图

---

## 1.2 项目定位：企业级智能对话和运维助手

`SuperBizAgent` 是一个面向企业的智能助手，主要解决两类问题：

### 第一类：知识库问答（RAG）

**场景**：新员工入职、运维手册查询、故障排查经验查询。

**示例对话**：
```
用户：CPU 使用率高怎么处理？
Agent：根据知识库，CPU 使用率高的处理步骤如下：
1. 查看 top 命令确认占用 CPU 的进程
2. 检查是否有异常进程或服务
3. ...
```

**核心能力**：
- 上传 Markdown/PDF/TXT 等文档
- 自动切分、向量化、存入向量数据库
- 用户提问时，先检索相关知识，再让 LLM 生成回答

### 第二类：AIOps 智能诊断

**场景**：线上服务出现告警，自动分析根因并给出处理建议。

**示例流程**：
```
用户：data-sync-service 出现告警，请排查
Agent：
1. 查询所有服务状态
2. 获取 data-sync-service 的 CPU、内存指标
3. 查询错误日志
4. 分析日志模式
5. 查询历史工单
6. 生成诊断报告
```

**核心能力**：
- 自动制定诊断计划（Planner）
- 调用日志、监控等工具执行步骤（Executor）
- 根据结果动态调整计划或生成报告（Replanner）

---

## 1.3 技术栈总览

| 层级 | 技术 | 作用 |
|------|------|------|
| Web 框架 | FastAPI | 提供 RESTful API |
| Agent 框架 | LangChain + LangGraph | 构建 Agent、工作流编排 |
| 大模型 | 阿里云 DashScope（通义千问） | 提供 LLM 和 Embedding 能力 |
| 向量数据库 | Milvus | 存储和检索向量化的文档 |
| 工具协议 | MCP（Model Context Protocol） | 标准化工具接入 |
| 包管理 | uv | 快速安装依赖、管理虚拟环境 |
| 容器化 | Docker + Docker Compose | 部署 Milvus 等基础设施 |
| 日志 | Loguru | 应用日志记录 |
| 前端 | 原生 HTML/JS/CSS | 提供 Web 交互界面 |

---

## 1.4 项目目录结构解读

```
super_biz_agent_py/
├── app/                                    # 应用核心
│   ├── main.py                             # FastAPI 应用入口
│   ├── config.py                           # 配置管理
│   ├── api/                                # API 路由层
│   │   ├── chat.py                         # 对话接口
│   │   ├── aiops.py                        # AIOps 接口
│   │   ├── file.py                         # 文件上传接口
│   │   └── health.py                       # 健康检查
│   ├── services/                           # 业务服务层
│   │   ├── rag_agent_service.py            # RAG Agent 核心
│   │   ├── aiops_service.py                # AIOps Plan-Execute-Replan
│   │   ├── vector_store_manager.py         # 向量存储管理
│   │   ├── vector_embedding_service.py     # Embedding 服务
│   │   ├── vector_index_service.py         # 文档索引服务
│   │   ├── vector_search_service.py        # 向量搜索服务
│   │   └── document_splitter_service.py    # 文档切分服务
│   ├── agent/                              # Agent 模块
│   │   ├── mcp_client.py                   # MCP 客户端
│   │   └── aiops/                          # AIOps 核心逻辑
│   │       ├── planner.py
│   │       ├── executor.py
│   │       ├── replanner.py
│   │       ├── state.py
│   │       └── utils.py
│   ├── models/                             # 数据模型
│   ├── tools/                              # Agent 工具集
│   │   ├── knowledge_tool.py
│   │   └── time_tool.py
│   ├── core/                               # 核心组件
│   │   ├── llm_factory.py                  # LLM 工厂
│   │   └── milvus_client.py                # Milvus 客户端
│   └── utils/                              # 工具类
│       └── logger.py                       # 日志配置
├── static/                                 # Web 前端
├── mcp_servers/                            # MCP 服务器
│   ├── cls_server.py                       # 日志查询服务
│   ├── monitor_server.py                   # 监控数据服务
│   └── README.md
├── aiops-docs/                             # 运维知识库文档
├── vector-database.yml                     # Milvus Docker Compose 配置
├── pyproject.toml                          # 项目依赖配置
├── start-windows.bat                       # Windows 一键启动
├── stop-windows.bat                        # Windows 一键停止
└── README.md
```

---

## 1.5 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         用户层                                │
│   Web 界面 (static/)   /   API 调用 (curl/scripts)          │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                    FastAPI 服务层                             │
│   /api/chat          /api/chat_stream      /api/aiops        │
│   /api/upload        /api/health                             │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
┌───────▼────────┐            ┌─────────▼──────────┐
│   RAG Agent    │            │   AIOps 诊断服务    │
│ LangGraph +    │            │ Plan-Execute-      │
│ ChatQwen +     │            │ Replan 工作流       │
│ Tools          │            │                    │
└───────┬────────┘            └─────────┬──────────┘
        │                               │
        │         ┌─────────────────────┘
        │         │
┌───────▼─────────▼──────────────────────────────────────────┐
│                      工具层                                  │
│  本地工具：knowledge_tool（知识库） / time_tool（时间）      │
│  MCP 工具：cls_server（日志） / monitor_server（监控）       │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                   基础设施层                                  │
│   LLM: DashScope (qwen-max)                                  │
│   Embedding: DashScope (text-embedding-v4)                   │
│   Vector DB: Milvus (Docker)                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 1.6 核心流程速览

### RAG 问答流程

```
用户提问
    │
    ▼
RAG Agent 接收问题
    │
    ▼
调用 knowledge_tool 检索向量库
    │
    ▼
将检索结果 + 问题一起传给 LLM
    │
    ▼
LLM 生成回答（支持流式输出）
```

### AIOps 诊断流程

```
用户触发诊断
    │
    ▼
Planner 制定诊断计划（4-6 步）
    │
    ▼
Executor 执行第 1 步 → 调用工具
    │
    ▼
Replanner 评估结果
    │
    ├── 还有步骤？→ 回到 Executor
    ├── 需要调整？→ 回到 Planner
    └── 完成？→ 生成诊断报告
```

---

## 1.7 本课作业

1. 通读 `README.md`，标注出不理解的名词。
2. 画出项目架构图（可手绘，也可用绘图工具）。
3. 列出项目中你最想深入学习的 3 个文件，并说明原因。

---

# 第 2 课：开发环境搭建（重点）

## 2.1 本课目标

通过本课学习，你能够：
- 独立完成项目的开发环境搭建
- 理解 `uv`、虚拟环境、`pyproject.toml` 的作用
- 成功启动 Milvus 向量数据库
- 解决 Windows 下常见的环境搭建问题

---

## 2.2 环境要求

| 组件 | 版本要求 | 说明 |
|------|---------|------|
| Python | 3.11 - 3.13 | 项目 `.python-version` 指定 3.13 |
| uv | 最新版 | 包管理器，比 pip 更快 |
| Docker Desktop | 最新版 | 运行 Milvus |
| Git Bash / CMD / PowerShell | - | 命令行工具 |
| 阿里云账号 | - | 获取 DashScope API Key |

**注意**：项目 `pyproject.toml` 中 `requires-python = ">=3.11,<3.14"`，所以 Python 3.10 不可用。

---

## 2.3 准备工作

### 2.3.1 获取 DashScope API Key

1. 访问 [阿里云 DashScope](https://dashscope.aliyun.com/)
2. 登录阿里云账号
3. 进入控制台 → API Key 管理
4. 创建新的 API Key
5. 复制保存（注意：Key 只显示一次，**不要泄露或写入文档中**）

> ⚠️ 安全提醒：API Key 等同于账号密码，请勿上传到公开仓库或共享文档。

DashScope 提供一定的免费额度，新手学习足够使用。

### 2.3.2 安装 Docker Desktop

1. 下载 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
2. 安装并启动
3. 确保 WSL2 后端正常运行
4. 在命令行执行 `docker ps` 测试是否成功

---

## 2.4 详细搭建步骤

### 步骤 1：进入项目目录

```bash
cd AgentProject/super_biz_agent_py-release-2026-05-17
```

**注意**：后续所有命令都在这个项目根目录下执行。

---

### 步骤 2：安装 uv 包管理器

```bash
pip install uv
```

`uv` 是一个用 Rust 编写的高性能 Python 包管理器，特点：
- 安装依赖速度极快
- 内置虚拟环境管理
- 支持 `uv.lock` 锁定依赖版本

如果你已经安装过 uv，可以跳过此步。

---

### 步骤 3：创建虚拟环境

```bash
uv venv
```

执行后会看到类似输出：
```
Using CPython 3.13.14
creating virtual environment at: .venv
Activate with: .venv\Scripts\activate
```

这会在项目目录下创建 `.venv` 文件夹，里面是一个独立的 Python 环境。

**为什么用虚拟环境？**
- 隔离项目依赖，避免污染系统 Python
- 不同项目可以用不同版本的包
- 便于迁移和复现

---

### 步骤 4：激活虚拟环境

**Windows Git Bash：**
```bash
source .venv/Scripts/activate
```

**Windows CMD：**
```cmd
.venv\Scripts\activate.bat
```

**Windows PowerShell：**
```powershell
.venv\Scripts\Activate.ps1
```

**Linux / macOS：**
```bash
source .venv/bin/activate
```

激活成功后，命令行前面会出现 `(.venv)` 标识：
```
(.venv) $
```

⚠️ **常见错误 1**：在 Git Bash 里写 `.venv\Scripts\activate`（用反斜杠），会被解析成 `.venvScriptsactivate`，报错找不到命令。

✅ **正确做法**：用正斜杠 `/`，或写 `source .venv/Scripts/activate`。

---

### 步骤 5：安装项目依赖

```bash
uv pip install -e .
```

**注意**：命令最后有一个 `.`（点），表示当前目录。

这会根据 `pyproject.toml` 安装所有依赖，包括：
- `fastapi`、`uvicorn`：Web 服务
- `langchain`、`langgraph`、`langchain-qwq`：Agent 框架
- `dashscope`：阿里云大模型
- `pymilvus`、`langchain-milvus`：向量数据库
- `fastmcp`、`langchain-mcp-adapters`：MCP 协议
- `loguru`：日志

`-e` 表示以 editable（可编辑）模式安装，这样你修改项目代码后不需要重新安装。

⚠️ **常见错误 2**：写成 `uv pip install -e`，漏掉最后的 `.`，会报错：
```
error: a value is required for '--editable <EDITABLE>' but none was supplied
```

✅ **正确做法**：`uv pip install -e .`

---

### 步骤 6：配置环境变量

项目根目录下有一个 `.env` 文件，打开它并填入你的 DashScope API Key：

```bash
notepad .env
```

关键配置项：

```ini
# DashScope 配置（必填）
DASHSCOPE_API_KEY=your-api-key-here
DASHSCOPE_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
DASHSCOPE_MODEL=qwen-max
DASHSCOPE_EMBEDDING_MODEL=text-embedding-v4

# Milvus 配置
MILVUS_HOST=localhost
MILVUS_PORT=19530

# RAG 配置
RAG_TOP_K=3
RAG_MODEL=qwen-max

# 文档分块配置
CHUNK_MAX_SIZE=800
CHUNK_OVERLAP=100

# MCP 服务配置
MCP_CLS_TRANSPORT=streamable-http
MCP_CLS_URL=http://localhost:8003/mcp
MCP_MONITOR_TRANSPORT=streamable-http
MCP_MONITOR_URL=http://localhost:8004/mcp
```

**必须把 `DASHSCOPE_API_KEY` 替换为你自己的真实 Key**，否则 LLM 调用会失败。

---

### 步骤 7：启动 Milvus 向量数据库

```bash
docker compose -f vector-database.yml up -d
```

这会启动三个容器：
- `milvus-etcd`：分布式协调服务
- `milvus-minio`：对象存储
- `milvus-standalone`：Milvus 主服务
- `milvus-attu`：Milvus Web 管理界面（可选）

等待约 10-30 秒，让服务完全启动。

验证启动成功：
```bash
docker ps
```

应该能看到 `milvus-standalone` 容器处于 `Up` 状态。

**Milvus 相关端口：**
- `19530`：Milvus 服务端口
- `9091`：Milvus 监控端口
- `8000`：Attu Web UI
- `9000/9001`：MinIO 控制台

---

### 步骤 8：验证安装

在虚拟环境中执行：

```bash
python -c "import app; print('导入成功')"
```

如果没有报错，说明依赖安装成功。

再测试一下关键依赖：
```bash
python -c "import langchain, langgraph, pymilvus, fastapi; print('核心依赖正常')"
```

---

## 2.5 使用一键启动脚本（推荐）

如果你不想手动执行每一步，Windows 下可以直接运行：

```cmd
start-windows.bat
```

这个脚本会自动完成：
1. 检查 uv 是否安装
2. 配置 Python 版本
3. 创建/同步虚拟环境
4. 启动 Milvus Docker 容器
5. 启动 CLS MCP 服务
6. 启动 Monitor MCP 服务
7. 启动 FastAPI 主服务
8. 上传 `aiops-docs/` 下的文档到向量库

停止服务：
```cmd
stop-windows.bat
```

**start-windows.bat 代码解读：**

```batch
@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
```
- `@echo off`：关闭命令回显
- `chcp 65001`：设置 UTF-8 编码，避免中文乱码
- `setlocal enabledelayedexpansion`：开启延迟变量扩展，用于在 if 块中读取变量

```batch
where uv >nul 2>&1
if errorlevel 1 (
    set USE_UV=0
) else (
    set USE_UV=1
)
```
- 检查 `uv` 是否已安装，决定后续使用 uv 还是传统 pip

```batch
if exist .python-version (
    set /p PYTHON_VERSION=<.python-version
    echo !PYTHON_VERSION! | findstr /C:"3.10" >nul
    if not errorlevel 1 (
        echo 3.13> .python-version
    )
)
```
- 读取 `.python-version` 文件中的 Python 版本
- 如果版本是 3.10（不兼容），自动更新为 3.13

```batch
docker ps --format "{{.Names}}" | findstr "milvus-standalone" >nul 2>&1
if not errorlevel 1 (
    echo Milvus 容器已在运行
) else (
    docker compose -f vector-database.yml up -d
    timeout /t 10 /nobreak >nul
)
```
- 检查 Milvus 是否已在运行，如果没有则启动并等待 10 秒

```batch
start "CLS MCP Server" /min %PYTHON_CMD% mcp_servers/cls_server.py
start "Monitor MCP Server" /min %PYTHON_CMD% mcp_servers/monitor_server.py
start "SuperBizAgent API" %PYTHON_CMD% -m uvicorn app.main:app --host 0.0.0.0 --port 9900
```
- 分别在新窗口中启动三个服务
- `/min` 表示最小化窗口启动

```batch
for %%f in (aiops-docs\*.md) do (
    curl -s -X POST http://localhost:9900/api/upload -F "file=@%%f" >nul 2>&1
)
```
- 遍历 `aiops-docs` 目录下的所有 Markdown 文件，上传到向量库

---

## 2.6 pyproject.toml 依赖配置解读

```toml
[project]
name = "super-biz-agent-py"
version = "1.2.1"
description = "基于 LangChain 的智能业务代理系统"
requires-python = ">=3.11,<3.14"
```

项目元信息：名称、版本、描述、Python 版本要求。

```toml
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "sse-starlette>=2.1.0",
    "langchain>=0.1.0",
    "langchain-community>=0.0.20",
    "langchain-core>=0.1.0",
    "langchain-openai>=1.0.0",
    "langgraph>=0.0.40",
    "dashscope>=1.14.0",
    "openai>=1.10.0",
    "pymilvus>=2.3.5",
    "pydantic>=2.5.0,<3.0.0",
    "pydantic-settings>=2.1.0",
    "langchain-milvus>=0.3.3",
    "langchain-text-splitters>=1.1.0",
    "langchain-mcp-adapters>=0.2.1",
    "fastmcp>=2.14.0",
    "langchain-qwq>=0.3.4",
]
```

核心依赖说明：

| 依赖 | 作用 |
|------|------|
| `fastapi` | Web 框架，提供 API |
| `uvicorn[standard]` | ASGI 服务器，运行 FastAPI |
| `sse-starlette` | 支持 Server-Sent Events 流式输出 |
| `langchain` | LangChain 核心库 |
| `langchain-core` | LangChain 核心抽象 |
| `langchain-openai` | OpenAI 兼容接口调用 |
| `langgraph` | 工作流图编排 |
| `dashscope` | 阿里云 DashScope SDK |
| `openai` | OpenAI SDK（用于兼容模式） |
| `pymilvus` | Milvus Python 客户端 |
| `langchain-milvus` | LangChain 与 Milvus 集成 |
| `langchain-text-splitters` | 文档切分 |
| `langchain-mcp-adapters` | LangChain 与 MCP 适配 |
| `fastmcp` | 快速构建 MCP 服务器 |
| `langchain-qwq` | 通义千问原生集成 |

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.3",
    "black>=23.12.0",
    "ruff>=0.1.9",
    "mypy>=1.8.0",
    "pre-commit>=3.6.0",
]
```

开发依赖，用于测试、格式化、代码检查。

---

## 2.7 vector-database.yml 解读

这是 Milvus 的 Docker Compose 配置文件。

```yaml
services:
  etcd:
    container_name: milvus-etcd
    image: quay.io/coreos/etcd:v3.5.18
```

**etcd**：分布式键值存储，Milvus 用它做服务发现和元数据存储。

```yaml
  minio:
    container_name: milvus-minio
    image: minio/minio:RELEASE.2023-03-20T20-16-18Z
    ports:
      - "9001:9001"
      - "9000:9000"
```

**MinIO**：对象存储，Milvus 用它存储向量数据和日志。

```yaml
  standalone:
    container_name: milvus-standalone
    image: milvusdb/milvus:v2.5.10
    command: ["milvus", "run", "standalone"]
    ports:
      - "19530:19530"
      - "9091:9091"
    depends_on:
      - "etcd"
      - "minio"
```

**standalone**：Milvus 单机模式主服务。
- `19530` 是对外提供向量服务的端口
- `depends_on` 确保 etcd 和 minio 先启动

```yaml
  attu:
    container_name: milvus-attu
    image: zilliz/attu:v2.5
    ports:
      - "8000:3000"
    environment:
      MILVUS_URL: standalone:19530
```

**Attu**：Milvus 的 Web 管理界面，访问 `http://localhost:8000` 可以查看 collection、数据等。

---

## 2.8 Windows 环境搭建常见问题

### 问题 1：激活虚拟环境失败

**错误信息：**
```
/usr/bin/bash: line 1: .venvScriptsactivate: command not found
```

**原因**：Git Bash 中反斜杠被吞掉了。

**解决**：
```bash
source .venv/Scripts/activate
```

### 问题 2：uv pip install -e 报错

**错误信息：**
```
error: a value is required for '--editable <EDITABLE>' but none was supplied
```

**原因**：缺少最后的 `.`。

**解决**：
```bash
uv pip install -e .
```

### 问题 3：Docker 启动失败

**错误信息：**
```
error during connect: This error may indicate that the docker daemon is not running
```

**原因**：Docker Desktop 没有启动。

**解决**：打开 Docker Desktop，等待其完全启动后再执行命令。

### 问题 4：端口被占用

**错误信息：**
```
Bind for 0.0.0.0:19530 failed: port is already allocated
```

**原因**：Milvus 或其他服务已经占用了端口。

**解决**：
```bash
# 查看占用端口的进程
netstat -ano | findstr :19530

# 结束进程（替换 PID）
taskkill /F /PID <PID>
```

### 问题 5：Python 版本不兼容

**错误信息：**
```
requires-python >=3.11,<3.14
```

**原因**：系统 Python 版本过低或过高。

**解决**：
```bash
# 安装 Python 3.11 - 3.13
# 然后指定版本创建虚拟环境
uv venv --python 3.13
```

### 问题 6：SSL 下载错误

**错误信息：**
```
SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] ...')
```

**原因**：网络不稳定或 SSL 连接中断。

**解决**：
- 重试命令
- 更换网络环境
- 配置 pip 国内镜像源

---

## 2.9 本课作业

1. 独立完成环境搭建，直到能执行 `python -c "import app; print('导入成功')"`。
2. 修改 `.env` 文件，填入自己的 DashScope API Key。
3. 启动 Milvus，用 `docker ps` 确认容器运行。
4. 访问 Attu Web UI（`http://localhost:8000`），看看能否连接上 Milvus。
5. 记录搭建过程中遇到的问题和解决方法。

---

# 第 3 课：服务启动与接口体验

## 3.1 本课目标

通过本课学习，你能够：
- 启动项目的所有服务
- 理解每个服务的作用
- 使用 Web 界面和 curl 测试接口
- 查看日志定位问题

---

## 3.2 服务组成

项目运行时需要启动以下服务：

| 服务 | 命令 | 端口 | 作用 |
|------|------|------|------|
| Milvus | `docker compose -f vector-database.yml up -d` | 19530 | 向量数据库 |
| CLS MCP | `python mcp_servers/cls_server.py` | 8003 | 日志查询工具 |
| Monitor MCP | `python mcp_servers/monitor_server.py` | 8004 | 监控数据工具 |
| FastAPI | `python -m uvicorn app.main:app --host 0.0.0.0 --port 9900` | 9900 | 主服务 |

---

## 3.3 手动启动所有服务

### 3.3.1 确保虚拟环境已激活

```bash
source .venv/Scripts/activate
```

### 3.3.2 启动 Milvus

```bash
docker compose -f vector-database.yml up -d
```

等待 10-30 秒。

### 3.3.3 启动 CLS MCP 服务

在新终端窗口执行：

```bash
cd AgentProject/super_biz_agent_py-release-2026-05-17
source .venv/Scripts/activate
python mcp_servers/cls_server.py
```

### 3.3.4 启动 Monitor MCP 服务

再开一个终端窗口：

```bash
cd AgentProject/super_biz_agent_py-release-2026-05-17
source .venv/Scripts/activate
python mcp_servers/monitor_server.py
```

### 3.3.5 启动 FastAPI 主服务

再开一个终端窗口：

```bash
cd AgentProject/super_biz_agent_py-release-2026-05-17
source .venv/Scripts/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 9900
```

### 3.3.6 上传文档

等 FastAPI 启动完成后，再开一个终端窗口：

```bash
cd AgentProject/super_biz_agent_py-release-2026-05-17
for f in aiops-docs/*.md; do
    curl -s -X POST http://localhost:9900/api/upload -F "file=@$f"
    echo " 上传完成: $f"
done
```

Windows CMD 可以用：
```cmd
for %f in (aiops-docs\*.md) do @curl -s -X POST http://localhost:9900/api/upload -F "file=@%f" && echo 上传完成: %f
```

---

## 3.4 使用一键启动脚本

更简单的方式是直接运行：

```cmd
start-windows.bat
```

这个脚本会按顺序启动所有服务，并自动上传文档。

停止所有服务：
```cmd
stop-windows.bat
```

---

## 3.5 服务启动后验证

### 3.5.1 健康检查

```bash
curl http://localhost:9900/health
```

预期返回：
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "SuperBizAgent"
}
```

### 3.5.2 查看 API 文档

打开浏览器访问：
```
http://localhost:9900/docs
```

这是 FastAPI 自动生成的 Swagger UI，可以：
- 查看所有接口
- 测试接口
- 查看请求/响应模型

---

## 3.6 接口体验

### 3.6.1 普通对话

```bash
curl -X POST "http://localhost:9900/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"Id":"session-001","Question":"你好，请介绍一下自己"}'
```

### 3.6.2 流式对话

```bash
curl -X POST "http://localhost:9900/api/chat_stream" \
  -H "Content-Type: application/json" \
  -d '{"Id":"session-001","Question":"CPU 使用率高怎么处理？"}' \
  --no-buffer
```

`--no-buffer` 让 curl 实时输出流式内容。

### 3.6.3 AIOps 诊断

```bash
curl -X POST "http://localhost:9900/api/aiops" \
  -H "Content-Type: application/json" \
  -d '{"session_id":"session-002"}' \
  --no-buffer
```

### 3.6.4 文件上传

```bash
curl -X POST "http://localhost:9900/api/upload" \
  -F "file=@aiops-docs/cpu_high_usage.md"
```

---

## 3.7 Web 界面体验

打开浏览器访问：
```
http://localhost:9900
```

界面通常包含：
- 普通对话模式
- 流式对话模式
- AIOps 智能运维模式
- 文件上传入口

尝试在不同模式下提问，观察：
1. RAG 模式是否会引用知识库内容？
2. 流式输出是如何逐步显示的？
3. AIOps 模式会执行哪些步骤？

---

## 3.8 日志查看

### FastAPI 主服务日志

```bash
# 查看当天日志
type logs\app_2026-06-26.log

# 查看最新日志
Get-ChildItem logs\*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content -Tail 50
```

### MCP 服务日志

```bash
type mcp_cls.log
type mcp_monitor.log
```

### 日志内容观察重点

1. **Agent 是否调用了工具？**
   ```
   调用 MCP 工具: query_cpu_metrics
   ```

2. **RAG 是否检索到了文档？**
   ```
   检索到 3 个相关文档
   ```

3. **AIOps 计划步骤**
   ```
   执行计划已制定，共 5 个步骤
   ```

---

## 3.9 常见问题排查

### 问题 1：MCP 服务连接失败

**现象**：Agent 无法调用工具，日志提示 MCP 连接错误。

**排查**：
1. 确认 CLS 和 Monitor 服务已启动
2. 确认 `.env` 中 MCP URL 正确
3. 检查端口 8003、8004 是否被占用

### 问题 2：Milvus 连接失败

**现象**：服务启动时报 `ConnectionNotExistException`。

**排查**：
```bash
docker ps | findstr milvus
```
确认 `milvus-standalone` 容器在运行。

### 问题 3：API Key 错误

**现象**：调用 `/api/chat` 返回 401 或模型调用失败。

**排查**：
```bash
type .env | findstr DASHSCOPE_API_KEY
```
确认 Key 已正确填入，且不是 `your-api-key-here`。

### 问题 4：文档上传后问答无效果

**现象**：RAG 问答说“没有找到相关信息”。

**排查**：
1. 确认文档已成功上传
2. 查看 Milvus Attu 中是否有 `biz` collection
3. 检查 `RAG_TOP_K` 配置

---

## 3.10 本课作业

1. 使用两种方式启动服务：手动逐个启动 + `start-windows.bat` 一键启动。
2. 用 curl 测试 `/api/chat`、`/api/chat_stream`、`/api/aiops` 三个接口。
3. 打开 Web 界面，分别用 RAG 模式和 AIOps 模式进行对话。
4. 查看 `logs/app_*.log`，找到一次工具调用的日志记录。
5. 尝试上传一个自己的 Markdown 文档，然后向 Agent 提问测试。

---

## 附录：启动命令速查表

| 操作 | Git Bash / Linux | Windows CMD |
|------|------------------|-------------|
| 激活虚拟环境 | `source .venv/Scripts/activate` | `.venv\Scripts\activate.bat` |
| 安装依赖 | `uv pip install -e .` | `uv pip install -e .` |
| 启动 Milvus | `docker compose -f vector-database.yml up -d` | `docker compose -f vector-database.yml up -d` |
| 启动 CLS MCP | `python mcp_servers/cls_server.py` | `python mcp_servers/cls_server.py` |
| 启动 Monitor MCP | `python mcp_servers/monitor_server.py` | `python mcp_servers/monitor_server.py` |
| 启动 FastAPI | `python -m uvicorn app.main:app --host 0.0.0.0 --port 9900` | `python -m uvicorn app.main:app --host 0.0.0.0 --port 9900` |
| 一键启动 | - | `start-windows.bat` |
| 一键停止 | - | `stop-windows.bat` |
| 健康检查 | `curl http://localhost:9900/health` | `curl http://localhost:9900/health` |
| API 文档 | `http://localhost:9900/docs` | `http://localhost:9900/docs` |
| Web 界面 | `http://localhost:9900` | `http://localhost:9900` |

---

*生成时间：2026/06/26*
