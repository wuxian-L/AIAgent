# AIAgent 项目实战课程 · 第 5 课详细讲义

# 配置管理与数据模型

> 课程基于 `AgentProject/super_biz_agent_py-release-2026-05-17` 项目
> 学习方式：理论 + 代码解读 + 动手实验
> 对应文件：`app/config.py`、`app/models/*.py`、`.env`

---

## 1. 本课目标

通过本课学习，你能够：

- 理解为什么要把配置从代码中抽离出来
- 掌握 `pydantic-settings` 的 `BaseSettings` 用法
- 理解 `.env` 文件与环境变量之间的映射关系
- 读懂项目 `app/config.py` 的每一个配置项
- 掌握 Pydantic `BaseModel` 的数据校验、别名、示例、可选字段
- 读懂 `app/models/` 下的请求/响应/AIOps/文档模型
- 能够在 `.env` 中新增自定义配置并在 `config.py` 中读取
- 能够编写简单的 Pydantic 模型并手动触发校验

---

## 2. 前置知识回顾

| 知识点 | 要求 | 说明 |
|--------|------|------|
| FastAPI 基础 | 掌握 | 上节课学习了应用创建、路由、中间件 |
| Pydantic 基础 | 了解 | 知道 `BaseModel`、类型注解、字段校验 |
| 环境变量 | 了解 | 知道 `.env`、`PATH`、`os.getenv` 基本概念 |
| Python 类型注解 | 了解 | `str`、`int`、`bool`、`Optional`、`List`、`Dict` 等 |

如果你还没看第 4 课，建议先回顾 `app/main.py` 是如何使用 `config.app_name`、`config.app_version` 等配置项的。

---

## 3. 为什么需要配置管理

### 3.1 硬编码配置的问题

初学者常犯的一个错误是把配置直接写在代码里：

```python
# ❌ 不好的写法
app = FastAPI(title="SuperBizAgent", version="1.0.0")
milvus_host = "localhost"
milvus_port = 19530
api_key = "sk-xxxxxxxx"
```

这样做的问题：

| 问题 | 说明 |
|------|------|
| 不安全 | API Key、密码等敏感信息会提交到 Git |
| 难维护 | 换一个环境（开发/测试/生产）就要改代码 |
| 易出错 | 多个地方硬编码同一配置，改一处漏一处 |
| 不方便协作 | 同事拉下代码后还要手动改配置 |

### 3.2 配置应该从哪里来

企业级项目通常把配置放到**环境**中：

```
环境变量  >  .env 文件  >  配置文件  >  代码默认值
```

在我们的项目里：

- `.env`：开发环境配置，不提交到 Git（通常加入 `.gitignore`）
- 环境变量：部署到服务器时由 CI/CD 或容器注入
- 代码默认值：`config.py` 中字段的默认值

### 3.3 Python 中读取配置的常见方式

| 方式 | 示例 | 缺点 |
|------|------|------|
| `os.getenv` | `os.getenv("APP_NAME", "SuperBizAgent")` | 无类型校验，全部返回字符串 |
| `python-dotenv` | `load_dotenv(); os.getenv(...)` | 需要手动加载，无类型转换 |
| `pydantic-settings` | `class Settings(BaseSettings)` | ✅ 自动加载 `.env`、自动类型转换、可校验 |

我们的项目使用 `pydantic-settings`，这是目前 Python 项目最推荐的配置管理方式。

---

## 4. Pydantic Settings 简介

### 4.1 安装

`pyproject.toml` 中已经包含：

```toml
"pydantic-settings>=2.1.0"
```

如果你创建新的项目，可以：

```bash
pip install pydantic-settings
```

### 4.2 最小示例

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    app_name: str = "MyApp"
    debug: bool = False
    port: int = 8000


config = Settings()
print(config.app_name)
print(config.debug)
print(config.port)
```

`.env` 文件内容：

```env
APP_NAME=SuperBizAgent
DEBUG=True
PORT=9900
```

运行后输出：

```
SuperBizAgent
True
9900
```

### 4.3 BaseSettings 会自动做什么

1. **读取 `.env` 文件**：根据 `env_file` 路径加载
2. **读取环境变量**：如果系统环境变量中存在，优先级更高
3. **自动类型转换**：把字符串 `"True"` 转成 `True`，`"9900"` 转成 `9900`
4. **使用默认值**：如果 `.env` 和环境变量都没有，使用字段默认值
5. **数据校验**：如果值类型不对，会抛出 `ValidationError`

### 4.4 SettingsConfigDict 常用参数

| 参数 | 说明 | 项目中的取值 |
|------|------|-------------|
| `env_file` | `.env` 文件路径 | `".env"` |
| `env_file_encoding` | 文件编码 | `"utf-8"` |
| `case_sensitive` | 是否区分大小写 | `False` |
| `extra` | 对未定义字段的处理 | `"ignore"` |

#### case_sensitive=False 的含义

环境变量通常习惯写成大写：

```env
DASHSCOPE_API_KEY=sk-xxx
```

而 Python 字段习惯小写：

```python
dashscope_api_key: str = ""
```

`case_sensitive=False` 时，`DASHSCOPE_API_KEY` 会自动映射到 `dashscope_api_key`。

#### extra="ignore" 的含义

如果 `.env` 里有一些配置在 `Settings` 类里没有定义，默认会报错。`extra="ignore"` 表示忽略这些未定义字段，不会报错。

例如 `.env` 里有 `PYTHONPATH=xxx`，但 `Settings` 里没有 `pythonpath` 字段，忽略即可。

---

## 5. 项目配置解读：`app/config.py`

### 5.1 完整代码

```python
"""配置管理模块

使用 Pydantic Settings 实现类型安全的配置管理
"""

from typing import Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 应用配置
    app_name: str = "SuperBizAgent"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 9900

    # DashScope 配置
    dashscope_api_key: str = ""  # 默认空字符串，实际使用需从环境变量加载
    dashscope_model: str = "qwen-max"
    dashscope_embedding_model: str = "text-embedding-v4"  # v4 支持多种维度（默认 1024）

    # Milvus 配置
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    milvus_timeout: int = 10000  # 毫秒

    # RAG 配置
    rag_top_k: int = 3
    rag_model: str = "qwen-max"  # 使用快速响应模型，不带扩展思考

    # 文档分块配置
    chunk_max_size: int = 800
    chunk_overlap: int = 100

    # MCP 服务配置（transport: stdio | sse | streamable-http）
    # 腾讯云托管 MCP 的 URL 通常含 /sse/，需使用 sse；本地 FastMCP 使用 streamable-http
    mcp_cls_transport: str = "streamable-http"
    mcp_cls_url: str = "http://localhost:8003/mcp"
    mcp_monitor_transport: str = "streamable-http"
    mcp_monitor_url: str = "http://localhost:8004/mcp"

    # Prometheus
    prometheus_base_url: str = "http://127.0.0.1:9090"
    prometheus_request_timeout: float = 10.0

    @property
    def mcp_servers(self) -> Dict[str, Dict[str, Any]]:
        """获取完整的 MCP 服务器配置"""
        return {
            "cls": {
                "transport": self.mcp_cls_transport,
                "url": self.mcp_cls_url,
            },
            "monitor": {
                "transport": self.mcp_monitor_transport,
                "url": self.mcp_monitor_url,
            }
        }


# 全局配置实例
config = Settings()
```

### 5.2 逐段分析

#### 导入部分

```python
from typing import Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
```

- `BaseSettings`：Pydantic Settings 的基类
- `SettingsConfigDict`：配置类的元配置
- `Dict`、`Any`：用于 `mcp_servers` 属性的类型注解

#### model_config

```python
model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    case_sensitive=False,
    extra="ignore",
)
```

这是 `Settings` 类的"配置的配置"：

- 从当前目录的 `.env` 文件加载
- 编码为 UTF-8，支持中文注释
- 不区分大小写，`MILVUS_HOST` 可以映射到 `milvus_host`
- 忽略未定义字段

#### 应用配置

```python
app_name: str = "SuperBizAgent"
app_version: str = "1.0.0"
debug: bool = False
host: str = "0.0.0.0"
port: int = 9900
```

对应 `.env`：

```env
APP_NAME=SuperBizAgent
DEBUG=True
HOST=0.0.0.0
PORT=9900
```

#### DashScope 配置

```python
dashscope_api_key: str = ""
dashscope_model: str = "qwen-max"
dashscope_embedding_model: str = "text-embedding-v4"
```

对应 `.env`：

```env
DASHSCOPE_API_KEY=sk-xxx
DASHSCOPE_MODEL=qwen-max
DASHSCOPE_EMBEDDING_MODEL=text-embedding-v4
```

`dashscope_api_key` 默认空字符串，因为代码里不能写死真实的 Key，必须从 `.env` 或环境变量加载。

#### Milvus 配置

```python
milvus_host: str = "localhost"
milvus_port: int = 19530
milvus_timeout: int = 10000  # 毫秒
```

对应 `.env`：

```env
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_TIMEOUT=10000
```

#### RAG 配置

```python
rag_top_k: int = 3
rag_model: str = "qwen-max"
```

`rag_top_k` 控制检索时返回多少个最相似的文档片段。值越大，上下文越多；值越小，噪声越少。

#### 文档分块配置

```python
chunk_max_size: int = 800
chunk_overlap: int = 100
```

- `chunk_max_size`：每个文档片段最大字符数
- `chunk_overlap`：相邻片段之间的重叠字符数

这两个参数会显著影响 RAG 的召回效果。

#### MCP 服务配置

```python
mcp_cls_transport: str = "streamable-http"
mcp_cls_url: str = "http://localhost:8003/mcp"
mcp_monitor_transport: str = "streamable-http"
mcp_monitor_url: str = "http://localhost:8004/mcp"
```

对应 `.env`：

```env
MCP_CLS_TRANSPORT=streamable-http
MCP_CLS_URL=http://localhost:8003/mcp
MCP_MONITOR_TRANSPORT=streamable-http
MCP_MONITOR_URL=http://localhost:8004/mcp
```

注释里也说明了三种 transport：

- `stdio`：标准输入输出，适合本地子进程
- `sse`：Server-Sent Events，腾讯云等托管 MCP 常用
- `streamable-http`：本地 FastMCP 默认方式

#### Prometheus 配置

```python
prometheus_base_url: str = "http://127.0.0.1:9090"
prometheus_request_timeout: float = 10.0
```

AIOps 诊断时可能需要查询 Prometheus 告警数据。

#### mcp_servers 属性

```python
@property
def mcp_servers(self) -> Dict[str, Dict[str, Any]]:
    """获取完整的 MCP 服务器配置"""
    return {
        "cls": {
            "transport": self.mcp_cls_transport,
            "url": self.mcp_cls_url,
        },
        "monitor": {
            "transport": self.mcp_monitor_transport,
            "url": self.mcp_monitor_url,
        }
    }
```

这是一个计算属性，把分散的 MCP 配置聚合成一个字典，方便传给 `MultiServerMCPClient`。后续课程会用到 `config.mcp_servers`。

#### 全局配置实例

```python
config = Settings()
```

程序启动时就会创建这个实例，其他模块通过 `from app.config import config` 来使用。

---

## 6. `.env` 文件解读

项目根目录的 `.env` 文件内容（节选）：

```env
# 应用配置
APP_NAME=SuperBizAgent
DEBUG=True
HOST=0.0.0.0
PORT=9900

# DashScope 配置
DASHSCOPE_API_KEY=sk-...
DASHSCOPE_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
DASHSCOPE_MODEL=qwen-max
DASHSCOPE_EMBEDDING_MODEL=text-embedding-v4

# Milvus 配置
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_TIMEOUT=10000

# RAG 配置
RAG_TOP_K=3
RAG_MODEL=qwen-max

# 文档分块配置
CHUNK_MAX_SIZE=800
CHUNK_OVERLAP=100

# MCP 服务配置
; MCP_CLS_TRANSPORT=sse
; MCP_CLS_URL=https://mcp-api.tencent-cloud.com/sse/xxxx
MCP_CLS_TRANSPORT=streamable-http
MCP_CLS_URL=http://localhost:8003/mcp
MCP_MONITOR_TRANSPORT=streamable-http
MCP_MONITOR_URL=http://localhost:8004/mcp

# Prometheus（告警查询工具等）
PROMETHEUS_BASE_URL=http://127.0.0.1:9090
PROMETHEUS_REQUEST_TIMEOUT=10.0
```

### 6.1 命名规则

由于 `case_sensitive=False`，环境变量名可以是：

```env
DASHSCOPE_MODEL=qwen-max
```

也可以是：

```env
dashscope_model=qwen-max
```

Pydantic Settings 都会映射到 `Settings.dashscope_model`。

### 6.2 注释

- `#` 开头的行是注释
- `;` 开头的行也是注释（dotenv 规范支持）

项目中用 `;` 注释掉了一套腾讯云的 MCP 配置，方便切换：

```env
; MCP_CLS_TRANSPORT=sse
; MCP_CLS_URL=https://...
```

取消注释并注释掉本地配置，就可以切换到腾讯云 MCP。

### 6.3 注意 `.env` 不应提交到 Git

`.env` 通常包含 API Key 等敏感信息，应该在 `.gitignore` 中忽略：

```gitignore
.env
```

---

## 7. 在应用中使用配置

### 7.1 导入全局配置

```python
from app.config import config

print(config.app_name)
print(config.host)
print(config.port)
```

### 7.2 在 `app/main.py` 中的使用

```python
from app.config import config

app = FastAPI(
    title=config.app_name,
    version=config.app_version,
    description="基于 LangChain 的智能oncall运维系统",
    lifespan=lifespan
)
```

`config.app_name` 和 `config.app_version` 都来自 `.env` 或默认值。

### 7.3 环境优先级

Pydantic Settings 的读取优先级（从高到低）：

1. 系统环境变量
2. `.env` 文件
3. 代码中的默认值

也就是说：

```bash
# 临时覆盖端口
$env:PORT=8888  # PowerShell
PORT=8888 python -m uvicorn app.main:app
```

即使 `.env` 里 `PORT=9900`，环境变量也能覆盖它。

---

## 8. Pydantic 数据模型

上一节课我们已经简单接触过 Pydantic。本课会系统学习它在项目中的四种用途：

| 用途 | 对应文件 | 说明 |
|------|---------|------|
| 请求模型 | `app/models/request.py` | 校验客户端发来的请求体 |
| 响应模型 | `app/models/response.py` | 规范返回给客户端的数据结构 |
| AIOps 模型 | `app/models/aiops.py` | AIOps 诊断专用请求/响应 |
| 文档模型 | `app/models/document.py` | 文档分片数据结构 |

### 8.1 BaseModel 基础

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str | None = None
```

创建实例：

```python
user = User(id=1, name="张三")
print(user.model_dump())
# {'id': 1, 'name': '张三', 'email': None}
```

如果类型不匹配：

```python
User(id="abc", name="张三")
```

会抛出 `ValidationError`：

```
1 validation error for User
id
  Input should be a valid integer, unable to parse string as an integer
```

### 8.2 Field 的常用参数

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    id: int = Field(..., description="用户 ID")
    name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(default=18, ge=0, le=150)
```

| 参数 | 说明 |
|------|------|
| `...` | 必填字段 |
| `default` / `default_factory` | 默认值 |
| `description` | 字段描述，会出现在 API 文档中 |
| `alias` | 字段别名，用于接收不同命名的 JSON 字段 |
| `ge` / `le` / `gt` / `lt` | 数值范围校验 |
| `min_length` / `max_length` | 字符串长度校验 |
| `json_schema_extra` | 为 Swagger 文档提供示例 |

### 8.3 别名 Alias

客户端可能发送这样的 JSON：

```json
{
  "Id": "session-123",
  "Question": "什么是向量数据库？"
}
```

但 Python 字段习惯小写：

```python
class ChatRequest(BaseModel):
    id: str = Field(..., alias="Id")
    question: str = Field(..., alias="Question")
```

为了让模型既接受别名也接受字段名，需要：

```python
class Config:
    populate_by_name = True
```

这样下面两种方式都能创建实例：

```python
ChatRequest(Id="session-123", Question="什么是向量数据库？")
ChatRequest(id="session-123", question="什么是向量数据库？")
```

---

## 9. 项目模型文件逐行解读

### 9.1 `app/models/__init__.py`

```python
"""数据模型模块"""
```

目前为空，只是标记 `app/models` 是一个 Python 包。后续可以在这里集中导出常用模型。

### 9.2 `app/models/request.py`

```python
"""请求数据模型

定义 API 请求的 Pydantic 模型
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """对话请求"""

    id: str = Field(..., description="会话 ID", alias="Id")
    question: str = Field(..., description="用户问题", alias="Question")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "Id": "session-123",
                "Question": "什么是向量数据库？"
            }
        }


class ClearRequest(BaseModel):
    """清空会话请求"""

    session_id: str = Field(..., description="会话 ID", alias="sessionId")

    class Config:
        populate_by_name = True
```

#### ChatRequest

| 字段 | 类型 | 是否必填 | 别名 | 说明 |
|------|------|---------|------|------|
| `id` | `str` | 是 | `Id` | 会话 ID |
| `question` | `str` | 是 | `Question` | 用户问题 |

`json_schema_extra` 为 Swagger 文档提供了示例请求体。

#### ClearRequest

| 字段 | 类型 | 是否必填 | 别名 | 说明 |
|------|------|---------|------|------|
| `session_id` | `str` | 是 | `sessionId` | 要清空的会话 ID |

---

### 9.3 `app/models/response.py`

```python
"""响应数据模型

定义 API 响应的 Pydantic 模型
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class ChatResponse(BaseModel):
    """对话响应"""

    answer: str = Field(..., description="AI 回答")
    session_id: str = Field(..., description="会话 ID")


class SessionInfoResponse(BaseModel):
    """会话信息响应"""

    session_id: str = Field(..., description="会话 ID")
    message_count: int = Field(..., description="消息数量")
    history: List[Dict[str, str]] = Field(..., description="历史消息列表")


class ApiResponse(BaseModel):
    """通用 API 响应"""

    status: str = Field(..., description="状态")
    message: str = Field(..., description="消息")
    data: Optional[Any] = Field(None, description="数据")


class HealthResponse(BaseModel):
    """健康检查响应"""

    status: str = Field(..., description="状态")
    service: str = Field(..., description="服务名称")
    version: str = Field(..., description="版本号")
```

#### ChatResponse

返回 AI 的回答和会话 ID：

```json
{
  "answer": "向量数据库是一种专门存储和检索高维向量的数据库...",
  "session_id": "session-123"
}
```

#### SessionInfoResponse

返回会话历史：

```json
{
  "session_id": "session-123",
  "message_count": 4,
  "history": [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！有什么可以帮你的？"}
  ]
}
```

#### ApiResponse

通用响应包装器：

```json
{
  "status": "success",
  "message": "文件上传成功",
  "data": {"filename": "ops.md"}
}
```

`data: Optional[Any]` 表示数据字段可有可无，类型任意。

#### HealthResponse

健康检查接口返回：

```json
{
  "status": "ok",
  "service": "SuperBizAgent",
  "version": "1.0.0"
}
```

---

### 9.4 `app/models/aiops.py`

```python
"""
AIOps 请求和响应模型
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AIOpsRequest(BaseModel):
    """AIOps 诊断请求"""
    
    session_id: Optional[str] = Field(
        default="default",
        description="会话ID，用于追踪诊断历史"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session-123"
            }
        }


class AlertInfo(BaseModel):
    """告警信息"""
    alertname: str
    severity: str
    instance: str
    duration: str
    description: Optional[str] = None


class DiagnosisResponse(BaseModel):
    """诊断响应（非流式）"""
    
    code: int = 200
    message: str = "success"
    data: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "success",
                "data": {
                    "status": "completed",
                    "target_alert": {
                        "alertname": "HighCPUUsage",
                        "severity": "critical"
                    },
                    "diagnosis": {
                        "root_cause": "数据库连接池耗尽",
                        "recommendations": ["扩容数据库连接池", "优化SQL查询"]
                    }
                }
            }
        }
```

#### AIOpsRequest

`session_id` 是可选的，默认 `"default"`。这意味着调用 `/api/aiops` 时可以不传 `session_id`。

```python
AIOpsRequest()  # session_id="default"
AIOpsRequest(session_id="session-123")
```

#### AlertInfo

描述一条告警信息：

```json
{
  "alertname": "HighCPUUsage",
  "severity": "critical",
  "instance": "192.168.1.10:9090",
  "duration": "5m",
  "description": "CPU 使用率超过 90%"
}
```

`description` 是可选的。

#### DiagnosisResponse

诊断结果响应，包含：

- `code`：HTTP 业务码，默认 200
- `message`：状态描述
- `data`：具体的诊断结果，结构任意

---

### 9.5 `app/models/document.py`

```python
"""文档相关数据模型"""

from typing import Optional

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    """文档分片模型"""

    content: str = Field(..., description="分片内容")
    start_index: int = Field(..., description="分片在原文档中的起始位置")
    end_index: int = Field(..., description="分片在原文档中的结束位置")
    chunk_index: int = Field(..., description="分片索引（从0开始）")
    title: Optional[str] = Field(None, description="分片所属章节标题")

    class Config:
        """Pydantic 配置"""
        json_schema_extra = {
            "example": {
                "content": "这是一段文档内容...",
                "start_index": 0,
                "end_index": 100,
                "chunk_index": 0,
                "title": "第一章",
            }
        }
```

`DocumentChunk` 表示文档被切分后的一个片段：

- `content`：片段内容
- `start_index` / `end_index`：在原文档中的位置
- `chunk_index`：片段编号
- `title`：所属章节标题（可选）

这个模型会在 `document_splitter_service.py` 中使用。

---

## 10. Pydantic 校验如何与 FastAPI 协作

FastAPI 会自动把 Pydantic 模型用于：

1. **请求体校验**：`async def chat(req: ChatRequest)`
2. **响应序列化**：`response_model=ChatResponse`
3. **自动生成文档**：`/docs` 里的 Swagger UI

示例：

```python
from fastapi import FastAPI
from app.models.request import ChatRequest
from app.models.response import ChatResponse

app = FastAPI()

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    return ChatResponse(
        answer=f"你问的是：{req.question}",
        session_id=req.id
    )
```

如果请求体不符合模型定义，FastAPI 会自动返回 422 错误：

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "Id"],
      "msg": "Field required"
    }
  ]
}
```

---

## 11. 动手实验

### 实验 1：在 `.env` 中新增自定义配置项

**目标**：新增一个 `APP_LOG_LEVEL` 配置，在 `config.py` 中读取并打印。

**步骤**：

1. 打开 `.env`，添加：

```env
APP_LOG_LEVEL=INFO
```

2. 打开 `app/config.py`，在 `Settings` 类中添加字段：

```python
log_level: str = "INFO"
```

3. 在项目根目录执行：

```bash
python -c "from app.config import config; print(config.log_level)"
```

预期输出：

```
INFO
```

4. 修改 `.env`：

```env
APP_LOG_LEVEL=DEBUG
```

再次执行，观察输出变为 `DEBUG`。

---

### 实验 2：手动验证 Pydantic 模型

**目标**：理解 Pydantic 的校验行为。

**步骤**：

1. 在项目根目录打开 Python：

```bash
python
```

2. 执行：

```python
from app.models.request import ChatRequest

# 正常创建
req = ChatRequest(Id="session-123", Question="你好")
print(req.model_dump())
print(req.model_dump(by_alias=True))

# 缺少必填字段
try:
    ChatRequest()
except Exception as e:
    print(e)
```

预期输出：

```python
{'id': 'session-123', 'question': '你好'}
{'Id': 'session-123', 'Question': '你好'}
```

以及一个 `ValidationError`，提示 `id` 和 `question` 是必填字段。

---

### 实验 3：修改响应模型并查看 Swagger 文档

**目标**：给 `app/api/health.py` 增加一个字段。

**步骤**：

1. 打开 `app/models/response.py`，给 `HealthResponse` 增加 `timestamp` 字段：

```python
from datetime import datetime

class HealthResponse(BaseModel):
    """健康检查响应"""

    status: str = Field(..., description="状态")
    service: str = Field(..., description="服务名称")
    version: str = Field(..., description="版本号")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="当前时间")
```

2. 启动服务：

```bash
python -m uvicorn app.main:app --reload
```

3. 访问 `http://localhost:9900/docs`，查看 `/health` 接口的响应 Schema。

4. 测试：

```bash
curl http://localhost:9900/health
```

---

## 12. 课后作业

### 必做作业

1. **阅读 `app/config.py` 和 `.env`**：把每个配置项的作用写成笔记，标注哪些有默认值、哪些必须从环境变量读取。

2. **新增自定义配置**：在 `.env` 中新增 `APP_LOG_LEVEL=DEBUG`，在 `config.py` 中读取，并打印验证。

3. **模型练习**：
   - 用 `ChatRequest` 创建 3 个不同实例
   - 故意传入错误类型，观察 `ValidationError`
   - 分别用 `model_dump()` 和 `model_dump(by_alias=True)` 输出，观察差异

### 选做作业

1. **新增一个配置类分组**：把 MCP 配置抽成单独的 `MCPSettings` 类，再用 `BaseSettings` 组合起来（提示：可以用嵌套模型或 Pydantic v2 的 `model_config`）。

2. **完善模型**：给 `DocumentChunk` 增加 `source`（来源文件）和 `metadata`（字典类型）字段，并写示例验证。

3. **响应模型实战**：在 `app/api/health.py` 中给健康检查接口加上 `response_model=HealthResponse`，并确保返回数据符合模型定义。

### 提交要求

- 记录实验截图和关键代码
- 写下至少 3 个本课学到的 Pydantic / pydantic-settings 知识点

---

## 13. 常见问题

### Q1：修改 `.env` 后配置没有生效

**原因**：`config = Settings()` 只在模块导入时创建一次，之后修改 `.env` 不会影响已加载的配置。

**解决**：重启服务，或在代码中重新实例化 `Settings()`。

### Q2：环境变量名和 Python 字段名对应不上

**原因**：可能是 `case_sensitive=True`，或者环境变量名和字段名差异太大。

**解决**：检查 `SettingsConfigDict` 的 `case_sensitive` 设置，或使用 `Field(..., env="MY_ENV_NAME")` 显式指定环境变量名。

### Q3：`.env` 里有未定义的字段就报错

**原因**：默认 `extra="forbid"`。

**解决**：在 `model_config` 中设置 `extra="ignore"`。

### Q4：FastAPI 返回 422 Unprocessable Entity

**原因**：请求体不符合 Pydantic 模型定义。

**解决**：查看错误详情中的 `loc` 字段，定位是哪个字段校验失败。常见原因：缺少必填字段、类型错误、使用了字段名而不是别名（未设置 `populate_by_name=True`）。

### Q5：`alias` 设置后，API 文档里显示的是别名还是字段名

**回答**：默认显示别名。如果你希望同时支持别名和字段名，一定要设置 `populate_by_name=True`。

---

## 14. 小结与下节课预告

### 本课小结

通过本课学习，你应该已经掌握：

- 为什么要把配置抽离到 `.env` 和环境变量
- `pydantic-settings` 的 `BaseSettings` 和 `SettingsConfigDict` 用法
- 项目 `app/config.py` 的完整结构和每个配置项含义
- `.env` 文件与环境变量的映射关系
- Pydantic `BaseModel` 的字段、别名、示例、可选值
- 项目 `app/models/` 下四类模型的作用
- Pydantic 如何与 FastAPI 配合完成请求校验和响应序列化

配置和数据模型是整个项目的"骨架"：配置决定了程序运行的环境，模型决定了接口输入输出的形状。理解它们是后续学习 LangChain、RAG、AIOps 的基础。

### 下节课预告

**第 6 课：LangChain 核心概念**

我们将学习：

- Model / Prompt / Output Parser
- Chain 的构建与运行
- LCEL（LangChain Expression Language）入门

请提前预习 `pyproject.toml` 中的 LangChain 依赖说明。

---

## 15. 参考资料

- [Pydantic 官方文档](https://docs.pydantic.dev/)
- [Pydantic Settings 文档](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [FastAPI 请求模型](https://fastapi.tiangolo.com/tutorial/body/)
- [FastAPI 响应模型](https://fastapi.tiangolo.com/tutorial/response-model/)
- [python-dotenv 文档](https://saurabh-kumar.com/python-dotenv/)

---

*生成时间：2026/06/30*  
*课程：AIAgent 项目实战 · 第 5 课*
