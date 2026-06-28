# AIAgent 项目实战课程 · 第 4 课详细讲义

# FastAPI 架构与应用入口

> 课程基于 `AgentProject/super_biz_agent_py-release-2026-05-17` 项目
> 学习方式：理论 + 代码解读 + 动手实验
> 对应文件：`app/main.py`、`app/api/health.py`、`app/config.py`、`app/models/request.py`

---

## 1. 本课目标

通过本课学习，你能够：

- 说清楚 FastAPI 的核心优势和适用场景
- 理解 FastAPI 的整体架构与请求处理流程
- 掌握 `FastAPI()` 应用创建、路由注册、中间件配置、静态文件挂载
- 掌握 `@asynccontextmanager` 生命周期管理（lifespan）
- 理解 CORS 中间件的作用与配置
- 能够阅读并解释项目 `app/main.py` 的每一行代码
- 独立在项目中新增一个测试接口

---

## 2. 前置知识回顾

在进入 FastAPI 之前，先确认你已经具备以下基础：

| 知识点 | 要求 | 说明 |
|--------|------|------|
| Python 异步编程 | 了解 | `async` / `await` 的基本用法 |
| HTTP 协议 | 了解 | 知道 GET / POST / PUT / DELETE 等动词、状态码 |
| RESTful API | 了解 | 资源定位、无状态通信 |
| JSON 数据格式 | 熟悉 | API 请求与响应的主要格式 |
| 类型注解 | 了解 | `def foo(x: int) -> str` 这种写法 |

如果你还不熟悉这些，建议先补充 Python 异步与 HTTP 基础，再继续本课。

---

## 3. 为什么选择 FastAPI

### 3.1 FastAPI 是什么

FastAPI 是一个现代、高性能的 Python Web 框架，用于构建 API。它基于以下两个核心库：

- **Starlette**：提供 ASGI 工具集、路由、中间件、请求/响应对象等底层能力
- **Pydantic**：提供数据验证、序列化、类型检查

FastAPI 站在两者的肩膀上，让开发者可以用很少的代码写出类型安全、自动文档、高性能的 API。

### 3.2 核心优势

| 优势 | 说明 | 对我们项目的意义 |
|------|------|------------------|
| **高性能** | 基于 Starlette 和 ASGI，性能接近 Node.js 和 Go | Agent 服务需要处理大量并发请求 |
| **类型安全** | 借助 Pydantic，请求参数、响应数据自动校验 | 减少运行时错误，接口更健壮 |
| **自动文档** | 自动生成 `/docs`（Swagger UI）和 `/redoc`（ReDoc） | 前后端联调、测试非常方便 |
| **异步原生** | 原生支持 `async` / `await` | LLM 调用、向量库查询都是 IO 密集型，异步能显著提升吞吐 |
| **依赖注入** | 内置强大的依赖注入系统 | 统一处理认证、数据库连接、配置等 |
| **生态成熟** | 与 LangChain、Uvicorn、Pydantic 等无缝集成 | 我们项目的技术栈天然契合 |

### 3.3 与其他框架对比

| 框架 | 特点 | 适用场景 |
|------|------|----------|
| Flask | 轻量、灵活、同步 | 小型项目、原型开发 |
| Django | 全栈、功能丰富、同步为主 | 大型 Web 应用、后台管理 |
| Tornado | 异步、长连接 | 实时应用 |
| **FastAPI** | **现代、异步、类型驱动、自动文档** | **API 服务、微服务、Agent 后端** |

我们项目选择 FastAPI 的原因：

1. 项目本质是提供 API 服务（聊天、文件上传、AIOps 诊断）
2. 需要大量异步 IO 操作（LLM 调用、Milvus 查询、MCP 工具调用）
3. 需要自动生成文档，方便前后端协作
4. LangChain、LangGraph 生态对 FastAPI 支持良好

---

## 4. FastAPI 架构全景

### 4.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        客户端（浏览器/脚本）                   │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP 请求
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      Uvicorn / Hypercorn                      │
│                 ASGI 服务器，处理网络连接                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI 应用层                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   路由层    │  │  中间件层   │  │   依赖注入系统      │  │
│  │ APIRouter   │  │ Middleware  │  │   Dependencies      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      业务处理层                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Pydantic   │  │  Service    │  │  LangChain /        │  │
│  │  数据校验   │  │  业务逻辑   │  │  LangGraph          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 请求处理流程

当一个 HTTP 请求进入 FastAPI 应用时，会经历以下步骤：

```
1. Uvicorn 接收 HTTP 请求
2. 请求到达 FastAPI 应用
3. 中间件链依次处理请求（如 CORS、日志、认证）
4. 路由匹配，找到对应的处理函数
5. 依赖注入系统解析依赖（如数据库连接、配置对象）
6. Pydantic 校验请求参数和请求体
7. 执行业务处理函数（可能是异步的）
8. Pydantic 序列化响应数据
9. 中间件链依次处理响应
10. 返回 HTTP 响应给客户端
```

理解这个流程很重要，因为后续定位问题（如参数校验失败、CORS 错误、响应格式不对）时，你知道应该看哪一层。

### 4.3 ASGI 是什么

ASGI（Asynchronous Server Gateway Interface）是 Python 异步 Web 应用的服务器网关接口标准。

你可以把它理解为应用和 Web 服务器之间的"通信协议"：

- **应用**（如 FastAPI）只关心业务逻辑
- **服务器**（如 Uvicorn）只关心网络连接、HTTP 解析
- ASGI 定义了两者如何交互

与传统的 WSGI（Flask、Django 早期版本使用）相比，ASGI 支持异步和 WebSocket，更适合现代高并发场景。

在我们的项目中，启动命令通常是这样的：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 9900 --reload
```

其中 `app.main:app` 表示：

- `app/main.py` 模块
- 该模块中的 `app` 变量（即 FastAPI 实例）

---

## 5. 核心概念速览

在学习具体代码之前，先认识 FastAPI 的几个核心概念：

| 概念 | 作用 | 本课涉及程度 |
|------|------|-------------|
| `FastAPI` 实例 | 应用的入口对象 | 重点 |
| `APIRouter` | 模块化路由 | 重点 |
| `lifespan` | 应用启动和关闭时的生命周期管理 | 重点 |
| `Middleware` | 请求/响应的拦截处理 | 重点 |
| `StaticFiles` | 静态文件服务 | 重点 |
| `Depends` | 依赖注入 | 了解 |
| `BaseModel` | Pydantic 数据模型 | 了解（下节课深入） |
| `BackgroundTasks` | 后台任务 | 了解 |

---

## 6. 创建 FastAPI 应用

### 6.1 最小 FastAPI 应用

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

保存为 `main.py`，然后启动：

```bash
uvicorn main:app --reload
```

访问 `http://127.0.0.1:8000/` 就能看到响应，访问 `http://127.0.0.1:8000/docs` 能看到自动生成的 API 文档。

### 6.2 FastAPI 构造函数常用参数

```python
app = FastAPI(
    title="SuperBizAgent",           # API 文档标题
    version="1.0.0",                 # 版本号
    description="基于 LangChain 的智能运维系统",  # 描述
    docs_url="/docs",                # Swagger UI 路径，默认 /docs
    redoc_url="/redoc",              # ReDoc 路径，默认 /redoc
    openapi_url="/openapi.json",     # OpenAPI Schema 路径
    lifespan=lifespan                # 生命周期管理函数
)
```

参数说明：

- `title` / `version` / `description`：用于自动生成 API 文档的元信息
- `docs_url` / `redoc_url`：可以自定义或关闭（设为 `None` 关闭）
- `lifespan`：应用启动和关闭时执行自定义逻辑，如连接数据库、加载模型

### 6.3 项目的应用创建

在我们项目中，`app/main.py` 是这样创建应用的：

```python
app = FastAPI(
    title=config.app_name,
    version=config.app_version,
    description="基于 LangChain 的智能oncall运维系统",
    lifespan=lifespan
)
```

这里从配置中读取应用名称和版本，并绑定了 `lifespan` 生命周期函数。

---

## 7. 生命周期管理：lifespan

### 7.1 为什么需要生命周期管理

一个 Web 应用在启动和关闭时，通常需要执行一些公共操作：

**启动时**：

- 连接数据库（Milvus、MySQL、Redis 等）
- 加载配置、模型、缓存
- 初始化日志
- 启动后台任务

**关闭时**：

- 关闭数据库连接
- 释放资源
- 保存状态

FastAPI 提供了 `lifespan` 机制来统一管理这些操作。

### 7.2 使用 @asynccontextmanager

FastAPI 推荐使用 `asynccontextmanager` 来定义 lifespan：

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    print("应用启动中...")
    await init_database()
    
    yield  # 应用运行期间
    
    # 关闭时执行
    print("应用关闭中...")
    await close_database()

app = FastAPI(lifespan=lifespan)
```

关键点：

- `yield` 之前的代码在应用启动时执行
- `yield` 之后的代码在应用关闭时执行
- `yield` 可以返回一个对象，供路由中通过 `request.state` 访问
- 必须是异步上下文管理器

### 7.3 旧版方式的对比

FastAPI 早期使用 `on_event("startup")` 和 `on_event("shutdown")`：

```python
@app.on_event("startup")
async def startup():
    await init_database()

@app.on_event("shutdown")
async def shutdown():
    await close_database()
```

**现在推荐用 `lifespan`，原因：**

1. 启动和关闭逻辑集中在一起，更容易维护
2. 支持依赖注入和状态传递
3. 更符合 ASGI 标准
4. `on_event` 在未来版本中可能被废弃

### 7.4 项目中的 lifespan 解读

看我们项目的 `app/main.py`：

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("=" * 60)
    logger.info(f"🚀 {config.app_name} v{config.app_version} 启动中...")
    logger.info(f"📝 环境: {'开发' if config.debug else '生产'}")
    logger.info(f"🌐 监听地址: http://{config.host}:{config.port}")
    logger.info(f"📚 API 文档: http://{config.host}:{config.port}/docs")
    
    # 连接 Milvus
    logger.info("🔌 正在连接 Milvus...")
    milvus_manager.connect()
    logger.info("✅ Milvus 连接成功")
    
    logger.info("=" * 60)
    
    yield
    
    # 关闭时执行
    logger.info("🔌 正在关闭 Milvus 连接...")
    milvus_manager.close()
    logger.info(f"👋 {config.app_name} 关闭")
```

逐行分析：

1. `@asynccontextmanager`：将 `lifespan` 函数转换为异步上下文管理器
2. `logger.info(...)`：输出启动日志，方便排查问题
3. `milvus_manager.connect()`：启动时连接 Milvus 向量数据库
4. `yield`：到这里应用开始接收请求
5. `milvus_manager.close()`：关闭时释放 Milvus 连接

**为什么 Milvus 连接放在 lifespan 里？**

- 避免每次请求都重新连接，提升性能
- 确保应用启动时就发现数据库问题，而不是等到第一次请求才报错
- 关闭时优雅释放资源，避免连接泄漏

---

## 8. 路由系统 APIRouter

### 8.1 为什么需要路由拆分

如果所有接口都写在 `main.py` 里，随着项目变大，文件会变得非常臃肿。FastAPI 提供了 `APIRouter` 来模块化组织路由。

### 8.2 APIRouter 基础用法

创建 `app/api/items.py`：

```python
from fastapi import APIRouter

router = APIRouter(prefix="/items", tags=["物品管理"])

@router.get("/")
async def list_items():
    return [{"id": 1, "name": "物品 A"}]

@router.get("/{item_id}")
async def get_item(item_id: int):
    return {"id": item_id, "name": "物品 A"}

@router.post("/")
async def create_item(name: str):
    return {"id": 2, "name": name}
```

在 `main.py` 中注册：

```python
from fastapi import FastAPI
from app.api import items

app = FastAPI()
app.include_router(items.router)
```

### 8.3 APIRouter 常用参数

| 参数 | 说明 |
|------|------|
| `prefix` | 该路由器下所有路由的前缀 |
| `tags` | API 文档中的分组标签 |
| `dependencies` | 该路由器下所有路由共享的依赖 |
| `responses` | 公共响应模型 |

示例：

```python
router = APIRouter(
    prefix="/api/users",
    tags=["用户管理"],
    dependencies=[Depends(get_current_user)]
)
```

### 8.4 项目中的路由注册

看 `app/main.py`：

```python
from app.api import chat, health, file, aiops

# 注册路由
app.include_router(health.router, tags=["健康检查"])
app.include_router(chat.router, prefix="/api", tags=["对话"])
app.include_router(file.router, prefix="/api", tags=["文件管理"])
app.include_router(aiops.router, prefix="/api", tags=["AIOps智能运维"])
```

这里：

- `health` 没有 `prefix`，因为健康检查通常是 `/health`
- `chat`、`file`、`aiops` 都加了 `/api` 前缀，所以它们的接口分别是：
  - `/api/chat`
  - `/api/upload`
  - `/api/aiops`

### 8.5 路径操作装饰器

FastAPI 提供与 HTTP 方法对应的装饰器：

```python
@app.get("/users")       # 查询
@app.post("/users")      # 创建
@app.put("/users/{id}")  # 全量更新
@app.patch("/users/{id}")# 部分更新
@app.delete("/users/{id}") # 删除
```

每个装饰器都可以接受参数：

```python
@app.get(
    "/users/{user_id}",
    summary="获取用户信息",
    description="根据用户 ID 返回用户详细信息",
    response_model=UserResponse,
    tags=["用户管理"]
)
async def get_user(user_id: int):
    ...
```

---

## 9. 请求与响应：Pydantic 模型

### 9.1 为什么需要 Pydantic

FastAPI 的强大之处在于与 Pydantic 的深度集成。Pydantic 负责：

- 自动校验请求参数类型
- 自动转换 JSON 为 Python 对象
- 自动生成 API 文档中的 Schema
- 序列化响应数据

### 9.2 基本示例

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str | None = None

@app.post("/users/")
async def create_user(user: User):
    return user
```

如果你发送的请求体是：

```json
{"id": "abc", "name": "张三"}
```

FastAPI 会自动返回 422 错误，因为 `id` 不是整数。

### 9.3 项目中的请求模型

看 `app/models/request.py`：

```python
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
```

这里有几个要点：

- `Field(...)` 中的 `...` 表示该字段是必填的
- `alias="Id"` 表示接口接收的 JSON 字段名是 `Id`（大写 I），但 Python 属性是 `id`
- `populate_by_name = True` 表示既可以用别名 `Id`，也可以用属性名 `id`
- `json_schema_extra` 为自动文档提供示例

### 9.4 响应模型

你可以用 `response_model` 指定响应结构：

```python
from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    name: str

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    return {"id": user_id, "name": "张三", "password": "secret"}
```

即使返回的字典包含 `password`，响应中也不会包含它，因为 `UserResponse` 没有这个字段。

---

## 10. 中间件

### 10.1 什么是中间件

中间件（Middleware）是拦截请求和响应的组件。每个请求进入应用时，会先经过中间件处理；响应返回客户端前，也会再次经过中间件。

常见用途：

- CORS 跨域处理
- 请求日志记录
- 认证与鉴权
- 请求耗时统计
- 错误统一处理

### 10.2 自定义中间件

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

说明：

- `request`：当前请求对象
- `call_next`：调用下一个中间件或路由处理函数
- 返回 `response`：可以继续修改响应

### 10.3 添加第三方中间件

```python
app.add_middleware(
    SomeMiddleware,
    param1="value1",
    param2="value2"
)
```

注意：中间件是按添加顺序执行的，但响应时是按相反顺序返回的。

---

## 11. CORS 配置

### 11.1 什么是 CORS

CORS（Cross-Origin Resource Sharing，跨源资源共享）是浏览器的安全机制。

当浏览器中的前端页面（如 `http://localhost:3000`）请求后端 API（如 `http://localhost:9900`）时，由于域名、端口或协议不同，浏览器会阻止请求，除非后端明确允许。

### 11.2 FastAPI 中配置 CORS

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

参数说明：

| 参数 | 说明 |
|------|------|
| `allow_origins` | 允许的源域名列表，`*` 表示允许所有 |
| `allow_credentials` | 是否允许携带 Cookie 等凭证 |
| `allow_methods` | 允许的 HTTP 方法 |
| `allow_headers` | 允许的请求头 |

### 11.3 项目中的 CORS

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**注意**：这里为了开发方便配置为 `*`，但生产环境一定要限制具体域名，否则有安全风险。

### 11.4 为什么需要 CORS

我们的项目有一个前端页面（`static/index.html`），它通过 JavaScript 调用 `/api/chat` 等接口。如果前后端端口不同，浏览器就会触发 CORS 检查。配置 CORS 后，前端才能正常访问后端 API。

---

## 12. 静态文件挂载

### 12.1 什么是静态文件

静态文件是指不需要后端动态生成的文件，如：

- HTML 页面
- CSS 样式
- JavaScript 脚本
- 图片、字体等

### 12.2 挂载静态文件

```python
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

参数说明：

- `/static`：URL 路径前缀
- `directory="static"`：本地文件夹路径
- `name="static"`：内部名称

这样，访问 `http://localhost:9900/static/app.js` 就会返回 `static/app.js` 文件。

### 12.3 项目中的静态文件

```python
static_dir = "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    """返回首页"""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": f"Welcome to {config.app_name} API",
        "version": config.app_version,
        "docs": "/docs"
    }
```

这里有两个要点：

1. `/static` 路径挂载了 `static` 目录，用于返回 CSS、JS 等资源
2. 根路径 `/` 返回 `static/index.html`，即项目的前端首页

如果 `index.html` 不存在，则返回 JSON 欢迎信息。

### 12.4 mount 与 include_router 的区别

| 方法 | 用途 | 示例 |
|------|------|------|
| `include_router` | 注册 API 路由 | `app.include_router(chat.router)` |
| `mount` | 挂载完整的子应用或静态文件 | `app.mount("/static", StaticFiles(...))` |

`mount` 更底层，适合挂载静态文件或其他 ASGI 应用。

---

## 13. 依赖注入系统

### 13.1 什么是依赖注入

依赖注入（Dependency Injection，DI）是一种设计模式，用来管理对象之间的依赖关系。

在 FastAPI 中，你可以把公共逻辑（如获取当前用户、数据库连接、配置对象）抽取成依赖函数，然后在多个路由中复用。

### 13.2 基础示例

```python
from fastapi import Depends, FastAPI

app = FastAPI()

async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    return commons
```

### 13.3 在我们项目中的应用

虽然 `app/main.py` 中没有直接使用 `Depends`，但项目的后续课程会大量用到依赖注入，例如：

- 获取配置对象
- 获取数据库连接
- 获取当前会话 ID
- 验证用户身份

建议先建立概念，后续课程再深入实践。

---

## 14. 异步处理

### 14.1 为什么 FastAPI 推荐异步

Web 应用中有大量 IO 操作（网络请求、数据库查询、文件读写）。如果使用同步方式，线程会在等待 IO 时被阻塞，无法处理其他请求。

异步编程允许一个线程在等待 IO 时去处理其他请求，从而显著提升并发能力。

### 14.2 async / await 基础

```python
import asyncio

async def say_hello():
    await asyncio.sleep(1)
    return "Hello"

async def main():
    result = await say_hello()
    print(result)

asyncio.run(main())
```

### 14.3 FastAPI 中的异步路由

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await fetch_user_from_db(user_id)  # 异步查询
    return user
```

### 14.4 什么时候用异步

| 场景 | 建议 |
|------|------|
| 调用异步库（如 httpx、aiomysql） | 用 `async` |
| 调用同步 IO 操作（如 requests、time.sleep） | 用同步函数，或用线程池包装 |
| 纯计算密集型任务 | 用后台任务或独立服务 |

在我们的项目中：

- Milvus 客户端调用
- LangChain / LangGraph 调用
- MCP 工具调用
- LLM API 调用

这些大多是 IO 密集型操作，非常适合异步。

---

## 15. 项目实战：app/main.py 完整解读

现在我们把目光聚焦到项目的 `app/main.py` 文件，逐段讲解。

### 15.1 完整代码

```python
"""FastAPI 应用入口

主应用程序，配置路由、中间件、静态文件等
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from app.config import config
from loguru import logger
from app.api import chat, health, file, aiops
from app.core.milvus_client import milvus_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("=" * 60)
    logger.info(f"🚀 {config.app_name} v{config.app_version} 启动中...")
    logger.info(f"📝 环境: {'开发' if config.debug else '生产'}")
    logger.info(f"🌐 监听地址: http://{config.host}:{config.port}")
    logger.info(f="📚 API 文档: http://{config.host}:{config.port}/docs")
    
    # 连接 Milvus
    logger.info("🔌 正在连接 Milvus...")
    milvus_manager.connect()
    logger.info("✅ Milvus 连接成功")
    
    logger.info("=" * 60)
    
    yield
    
    # 关闭时执行
    logger.info("🔌 正在关闭 Milvus 连接...")
    milvus_manager.close()
    logger.info(f"👋 {config.app_name} 关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=config.app_name,
    version=config.app_version,
    description="基于 LangChain 的智能oncall运维系统",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router, tags=["健康检查"])
app.include_router(chat.router, prefix="/api", tags=["对话"])
app.include_router(file.router, prefix="/api", tags=["文件管理"])
app.include_router(aiops.router, prefix="/api", tags=["AIOps智能运维"])

# 挂载静态文件
static_dir = "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    """返回首页"""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": f"Welcome to {config.app_name} API",
        "version": config.app_version,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=config.host,
        port=config.port,
        reload=config.debug,
        log_level="info"
    )
```

### 15.2 模块导入分析

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from app.config import config
from loguru import logger
from app.api import chat, health, file, aiops
from app.core.milvus_client import milvus_manager
```

导入分三类：

1. **FastAPI 内置模块**：应用、中间件、静态文件、响应类
2. **Python 标准库**：异步上下文管理器、操作系统路径
3. **项目内部模块**：配置、日志、API 路由、Milvus 管理器

### 15.3 生命周期函数分析

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
```

- 这是一个异步上下文管理器
- 参数 `app` 是 FastAPI 实例
- `yield` 之前是启动逻辑
- `yield` 之后是关闭逻辑

启动时做了四件事：

1. 打印启动日志（应用名、版本、环境、监听地址、文档地址）
2. 连接 Milvus 向量数据库
3. 进入运行状态
4. 关闭时释放 Milvus 连接

### 15.4 应用实例分析

```python
app = FastAPI(
    title=config.app_name,
    version=config.app_version,
    description="基于 LangChain 的智能oncall运维系统",
    lifespan=lifespan
)
```

这里创建了 FastAPI 应用实例，并：

- 设置应用名、版本、描述（用于自动文档）
- 绑定 lifespan 函数

### 15.5 中间件分析

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- 添加了 CORS 中间件
- 开发环境允许所有来源，方便调试
- 生产环境必须改为具体域名

### 15.6 路由注册分析

```python
app.include_router(health.router, tags=["健康检查"])
app.include_router(chat.router, prefix="/api", tags=["对话"])
app.include_router(file.router, prefix="/api", tags=["文件管理"])
app.include_router(aiops.router, prefix="/api", tags=["AIOps智能运维"])
```

| 路由模块 | URL 前缀 | 标签 |
|---------|---------|------|
| health | 无 | 健康检查 |
| chat | `/api` | 对话 |
| file | `/api` | 文件管理 |
| aiops | `/api` | AIOps智能运维 |

### 15.7 静态文件与首页

```python
static_dir = "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": f"Welcome to {config.app_name} API",
        "version": config.app_version,
        "docs": "/docs"
    }
```

- `/static` 提供静态资源
- `/` 返回前端首页 `index.html`
- 如果首页不存在，返回 JSON 欢迎信息

### 15.8 启动入口分析

```python
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=config.host,
        port=config.port,
        reload=config.debug,
        log_level="info"
    )
```

- 当直接运行 `python app/main.py` 时执行
- `reload=config.debug`：开发环境自动重载，生产环境关闭
- `log_level="info"`：日志级别

实际项目中更常用命令行启动：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 9900 --reload
```

---

## 16. 动手实验

### 实验 1：新增一个 /api/hello 测试接口

**目标**：在 `app/main.py` 中新增一个 `/api/hello` 接口，支持接收名字参数。

**步骤**：

1. 打开 `app/main.py`
2. 在路由注册之后、静态文件挂载之前，添加以下代码：

```python
@app.get("/api/hello")
async def hello(name: str = "实习生"):
    """测试接口：打招呼"""
    return {
        "message": f"你好，{name}！欢迎学习 FastAPI",
        "framework": "FastAPI",
        "version": config.app_version
    }
```

3. 启动服务：

```bash
uvicorn app.main:app --reload
```

4. 测试接口：

```bash
curl "http://localhost:9900/api/hello?name=小明"
```

预期响应：

```json
{
  "message": "你好，小明！欢迎学习 FastAPI",
  "framework": "FastAPI",
  "version": "1.0.0"
}
```

5. 打开 `http://localhost:9900/docs`，查看自动生成的接口文档

### 实验 2：查看生命周期日志

**目标**：观察 lifespan 的启动和关闭日志。

**步骤**：

1. 启动服务
2. 查看控制台输出的启动日志
3. 按 `Ctrl+C` 停止服务
4. 观察关闭日志

### 实验 3：测试 CORS

**目标**：验证 CORS 配置是否生效。

**步骤**：

1. 创建一个简单的 HTML 文件 `test_cors.html`：

```html
<!DOCTYPE html>
<html>
<head>
    <title>CORS Test</title>
</head>
<body>
    <button onclick="testCors()">测试 CORS</button>
    <div id="result"></div>
    <script>
        async function testCors() {
            try {
                const res = await fetch('http://localhost:9900/api/hello?name=前端');
                const data = await res.json();
                document.getElementById('result').innerText = JSON.stringify(data);
            } catch (e) {
                document.getElementById('result').innerText = '错误: ' + e.message;
            }
        }
    </script>
</body>
</html>
```

2. 用浏览器打开这个 HTML 文件
3. 点击按钮，观察是否能正常获取数据
4. 如果去掉 CORS 配置，会报什么错误？

---

## 17. 课后作业

### 必做作业

1. **阅读并解释代码**：逐行解释 `app/main.py` 中每一部分的作用，写成笔记。

2. **新增测试接口**：在 `app/main.py` 中新增一个 `/api/hello` 接口，要求：
   - 支持 `GET` 方法
   - 接收 `name` 查询参数，默认值为 "实习生"
   - 返回包含问候语、框架名、应用版本的 JSON

3. **查看自动文档**：启动服务后访问 `/docs`，找到你新增的接口，尝试用 Swagger UI 调用它。

### 选做作业

1. **自定义中间件**：新增一个记录请求耗时的中间件，在响应头中添加 `X-Process-Time`。

2. **限制 CORS**：将 `allow_origins=["*"]` 改为只允许 `http://localhost:3000`，验证前端是否能正常访问。

3. **健康检查理解**：阅读 `app/api/health.py`，理解健康检查接口如何判断服务状态。

### 提交要求

- 将你的代码修改和实验截图保存到学习笔记
- 写下至少 3 个你在本课中学到的 FastAPI 知识点

---

## 18. 常见问题

### Q1：启动时报 "ModuleNotFoundError: No module named 'app'"

**原因**：Python 找不到 `app` 模块。

**解决**：在项目根目录下启动，使用：

```bash
uvicorn app.main:app --reload
```

如果还不行，检查是否在正确的虚拟环境中，以及 `app/__init__.py` 是否存在。

### Q2：CORS 配置不生效

**原因**：可能是浏览器缓存，或者请求在到达 CORS 中间件前就失败了。

**解决**：

- 确认 `app.add_middleware(CORSMiddleware, ...)` 在路由注册之前
- 检查 `allow_origins` 是否包含前端域名
- 查看浏览器控制台的错误信息

### Q3：lifespan 中的代码没有执行

**原因**：可能是使用了 `on_event` 与 `lifespan` 混用，或者 ASGI 服务器不支持。

**解决**：

- 不要混用 `on_event` 和 `lifespan`
- 确保 Uvicorn 版本较新
- 检查是否有异常被吞掉

### Q4：静态文件访问 404

**原因**：`static` 目录不存在，或路径配置错误。

**解决**：

- 确认项目根目录下有 `static` 文件夹
- 确认 `app.mount("/static", StaticFiles(directory="static"), name="static")` 中的路径正确

---

## 19. 小结与下节课预告

### 本课小结

通过本课学习，你应该已经掌握：

- FastAPI 的核心优势和架构
- 如何创建 FastAPI 应用实例
- 使用 `lifespan` 管理应用生命周期
- 使用 `APIRouter` 组织路由
- 配置 CORS 中间件
- 挂载静态文件
- 阅读和理解项目 `app/main.py`

FastAPI 是我们整个 Agent 项目的"门面"，所有外部请求都通过它进入系统。理解它的工作原理，是后续学习 LangChain、RAG、AIOps 的基础。

### 下节课预告

**第 5 课：配置管理与数据模型**

我们将学习：

- `pydantic-settings` 环境变量管理
- `BaseSettings` 配置类
- Pydantic 模型：`request.py`、`response.py`、`aiops.py`、`document.py`

请提前预习 `app/config.py` 和 `app/models/` 目录下的文件。

---

## 20. 参考资料

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [FastAPI 教程 - 中文](https://fastapi.tiangolo.com/zh/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [Uvicorn 文档](https://www.uvicorn.org/)
- [Starlette 文档](https://www.starlette.io/)
- [ASGI 规范](https://asgi.readthedocs.io/)

---

*生成时间：2026/06/28*
*讲师：架构师*
*课程：AIAgent 项目实战 · 第 4 课*
