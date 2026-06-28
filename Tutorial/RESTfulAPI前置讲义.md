# AIAgent 前置知识补充讲义 · RESTful API 基础

> 本讲义为 AIAgent 项目实战课程的前置知识补充
> 目标：掌握 RESTful API 的设计思想、HTTP 方法、状态码和请求响应规范
> 建议学习时长：60-90 分钟（理论 + 实验）

---

## 1. 什么是 API

API（Application Programming Interface，应用程序编程接口）是软件之间交互的约定。

你可以把 API 理解成"服务员"：

- 你（客户端）向服务员点菜（发送请求）
- 服务员把需求传给厨房（服务器处理）
- 服务员把菜端给你（返回响应）

在 Web 开发中，API 通常指 **Web API**，即通过 HTTP 协议进行通信的接口。

---

## 2. 什么是 RESTful API

REST（Representational State Transfer，表现层状态转移）是一种设计 Web API 的风格，由 Roy Fielding 在 2000 年提出。

RESTful API 的核心思想：**把网络上的所有事物都抽象为资源，通过统一的接口对资源进行操作。**

### 2.1 REST 的六个核心原则

| 原则 | 说明 |
|------|------|
| **1. 客户端-服务器架构** | 客户端和服务器分离，各自独立演进 |
| **2. 无状态** | 服务器不保存客户端的状态，每次请求都包含完整信息 |
| **3. 可缓存** | 响应可以被客户端或中间层缓存 |
| **4. 统一接口** | 使用统一的资源标识和操作方法 |
| **5. 分层系统** | 客户端不需要知道是直连服务器还是经过代理/网关 |
| **6. 按需代码（可选）** | 服务器可以返回可执行代码（实际中较少用） |

对我们项目最重要的是：**资源抽象、统一接口、无状态**。

---

## 3. RESTful API 的核心要素

### 3.1 资源（Resource）

资源是 REST 的核心概念。任何可以被命名的事物都可以是资源：

- 用户（user）
- 订单（order）
- 文档（document）
- 会话（session）

每个资源都有一个唯一的标识符：**URL**。

### 3.2 URL 设计

RESTful API 使用 URL 来定位资源，URL 中一般只包含名词，不包含动词。

| 非 RESTful（不好） | RESTful（好） |
|-------------------|--------------|
| `/getUser?id=1` | `GET /users/1` |
| `/createUser` | `POST /users` |
| `/deleteUser?id=1` | `DELETE /users/1` |
| `/updateUser` | `PUT /users/1` 或 `PATCH /users/1` |

设计规则：

1. 使用名词复数形式，如 `/users`、`/orders`
2. 使用斜杠 `/` 表示层级关系，如 `/users/1/orders`
3. URL 中不使用大写，如 `/userOrders` 不好，应用 `/user-orders`
4. 不使用文件扩展名，如 `/users/1.json` 不推荐

### 3.3 HTTP 方法

RESTful API 通过 HTTP 方法（动词）来表示对资源的操作：

| HTTP 方法 | 含义 | 示例 | 是否幂等* |
|-----------|------|------|----------|
| `GET` | 获取资源 | `GET /users/1` | 是 |
| `POST` | 创建资源 | `POST /users` | 否 |
| `PUT` | 全量更新资源 | `PUT /users/1` | 是 |
| `PATCH` | 部分更新资源 | `PATCH /users/1` | 否 |
| `DELETE` | 删除资源 | `DELETE /users/1` | 是 |

*幂等：多次执行同样的操作，结果相同。

### 3.4 请求与响应

一次完整的 API 调用包含：

**请求（Request）：**

- HTTP 方法
- URL（资源路径）
- Headers（请求头，如 Content-Type、Authorization）
- Body（请求体，POST/PUT/PATCH 通常有）

**响应（Response）：**

- 状态码（Status Code）
- Headers（响应头）
- Body（响应体，通常是 JSON）

---

## 4. HTTP 状态码

状态码用于表示请求处理的结果。记住常用的几类即可：

### 2xx：成功

| 状态码 | 含义 | 说明 |
|--------|------|------|
| 200 | OK | 请求成功，通用成功状态 |
| 201 | Created | 资源创建成功 |
| 204 | No Content | 请求成功，但响应体为空 |

### 3xx：重定向

| 状态码 | 含义 | 说明 |
|--------|------|------|
| 301 | Moved Permanently | 永久重定向 |
| 302 | Found | 临时重定向 |
| 304 | Not Modified | 资源未修改，可使用缓存 |

### 4xx：客户端错误

| 状态码 | 含义 | 说明 |
|--------|------|------|
| 400 | Bad Request | 请求参数错误或格式不对 |
| 401 | Unauthorized | 未认证 |
| 403 | Forbidden | 无权限 |
| 404 | Not Found | 资源不存在 |
| 422 | Unprocessable Entity | 请求格式正确，但语义有误（FastAPI/Pydantic 常用） |

### 5xx：服务器错误

| 状态码 | 含义 | 说明 |
|--------|------|------|
| 500 | Internal Server Error | 服务器内部错误 |
| 502 | Bad Gateway | 网关错误 |
| 503 | Service Unavailable | 服务暂时不可用 |

### 4.1 项目中的应用

看我们项目的 `app/api/health.py`：

```python
if health_data["milvus"]["status"] != "connected":
    overall_status = "unhealthy"
    status_code = 503
    health_data["error"] = "数据库不可用"
```

这里当数据库不可用时返回 **503**，表示服务暂时不可用，这是正确的做法。

---

## 5. 请求方法详解

### 5.1 GET：获取资源

用于从服务器获取数据，不应该产生副作用。

```bash
curl -X GET "http://localhost:9900/api/users/1"
```

响应示例：

```json
{
  "id": 1,
  "name": "张三",
  "email": "zhangsan@example.com"
}
```

### 5.2 POST：创建资源

用于在服务器上创建新资源。

```bash
curl -X POST "http://localhost:9900/api/users" \
  -H "Content-Type: application/json" \
  -d '{"name":"李四","email":"lisi@example.com"}'
```

响应示例（201 Created）：

```json
{
  "id": 2,
  "name": "李四",
  "email": "lisi@example.com"
}
```

### 5.3 PUT：全量更新

用于完整替换资源。客户端需要提供资源的完整表示。

```bash
curl -X PUT "http://localhost:9900/api/users/1" \
  -H "Content-Type: application/json" \
  -d '{"name":"张三三","email":"zhangsan@example.com"}'
```

### 5.4 PATCH：部分更新

用于部分修改资源。客户端只需要提供要修改的字段。

```bash
curl -X PATCH "http://localhost:9900/api/users/1" \
  -H "Content-Type: application/json" \
  -d '{"name":"张三三"}'
```

### 5.5 DELETE：删除资源

用于删除服务器上的资源。

```bash
curl -X DELETE "http://localhost:9900/api/users/1"
```

---

## 6. 请求头与 Content-Type

### 6.1 常见请求头

| Header | 说明 |
|--------|------|
| `Content-Type` | 请求体格式，如 `application/json` |
| `Accept` | 客户端希望接收的响应格式 |
| `Authorization` | 认证信息，如 `Bearer token` |
| `User-Agent` | 客户端标识 |

### 6.2 Content-Type 常用值

| 值 | 含义 |
|---|------|
| `application/json` | JSON 数据 |
| `application/x-www-form-urlencoded` | 表单数据 |
| `multipart/form-data` | 上传文件 |
| `text/plain` | 纯文本 |
| `text/html` | HTML 文档 |

在我们的项目中，普通接口用 `application/json`，文件上传用 `multipart/form-data`。

---

## 7. 无状态原则

### 7.1 什么是无状态

**无状态（Stateless）** 是指服务器不保存客户端的任何状态信息。每个请求都必须包含服务器处理该请求所需的全部信息。

### 7.2 有状态 vs 无状态

**有状态：**

```
客户端：登录
服务器：创建 session，记住用户已登录
客户端：请求数据（只带 session id）
服务器：根据 session 判断用户身份
```

**无状态：**

```
客户端：登录，获取 token
客户端：每次请求都带上 token
服务器：根据 token 验证身份，不保存 session
```

### 7.3 为什么 REST 要无状态

1. **可扩展性**：任何服务器实例都可以处理任何请求，便于水平扩展
2. **可靠性**：服务器宕机后，客户端状态不会丢失
3. **简单性**：服务器不需要维护复杂的会话状态

在我们的 Agent 项目中，虽然没有登录认证，但会话管理也遵循类似思想：

- 每次对话请求都带上 `session_id`（即 `Id`）
- 服务器根据 `session_id` 从存储中恢复会话历史
- 服务器本身不长期保持某个客户端的内存状态

---

## 8. 响应数据格式

RESTful API 的响应通常是 JSON 格式。一个良好的响应应该结构统一。

### 8.1 统一响应结构

常见格式：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": 1,
    "name": "张三"
  }
}
```

或简洁格式：

```json
{
  "id": 1,
  "name": "张三"
}
```

### 8.2 错误响应

```json
{
  "code": 400,
  "message": "参数错误：name 不能为空",
  "data": null
}
```

### 8.3 项目中的响应

看项目的 `app/api/health.py`：

```python
return JSONResponse(
    status_code=status_code,
    content={
        "code": status_code,
        "message": "服务运行正常" if overall_status == "healthy" else "服务不可用",
        "data": health_data
    }
)
```

这里采用了 `{code, message, data}` 的统一响应结构，这是我们项目的风格。

---

## 9. RESTful API 设计实战

### 9.1 设计一个用户管理系统

假设要设计用户管理接口：

| 操作 | HTTP 方法 | URL | 说明 |
|------|-----------|-----|------|
| 查询用户列表 | GET | `/users` | 可带分页参数 `?page=1&size=10` |
| 查询单个用户 | GET | `/users/{id}` | |
| 创建用户 | POST | `/users` | 请求体包含用户信息 |
| 更新用户 | PUT | `/users/{id}` | 全量更新 |
| 删除用户 | DELETE | `/users/{id}` | |

### 9.2 设计一个博客系统

| 操作 | HTTP 方法 | URL |
|------|-----------|-----|
| 查询文章列表 | GET | `/articles` |
| 查询单篇文章 | GET | `/articles/{id}` |
| 创建文章 | POST | `/articles` |
| 更新文章 | PUT | `/articles/{id}` |
| 删除文章 | DELETE | `/articles/{id}` |
| 查询文章评论 | GET | `/articles/{id}/comments` |
| 发表评论 | POST | `/articles/{id}/comments` |

### 9.3 过滤、排序、分页

通过查询参数实现：

```
GET /users?role=admin&sort=created_at&order=desc&page=1&size=20
```

---

## 10. 在我们项目中的应用

### 10.1 项目接口速览

| 接口 | HTTP 方法 | URL | 功能 |
|------|-----------|-----|------|
| 健康检查 | GET | `/health` | 检查服务状态 |
| 对话 | POST | `/api/chat` | 普通对话 |
| 流式对话 | POST | `/api/chat_stream` | SSE 流式输出 |
| 清空会话 | POST | `/api/clear` | 清空指定会话 |
| 上传文件 | POST | `/api/upload` | 上传知识库文档 |
| AIOps 诊断 | POST | `/api/aiops` | 智能运维诊断 |
| AIOps 流式诊断 | POST | `/api/aiops/stream` | 流式诊断输出 |

### 10.2 项目接口设计分析

这些接口基本符合 RESTful 风格：

- 使用名词资源：`/chat`、`/upload`、`/aiops`
- 使用 HTTP 方法区分操作：POST 用于创建/执行动作
- 响应统一格式：`{code, message, data}`

当然，像 `/api/chat` 这种"对话"操作不是典型的 CRUD 资源，实际中会把它抽象为"创建一条对话消息"或"执行一次对话"。

---

## 11. FastAPI 中的 RESTful 实践

### 11.1 基础 CRUD 示例

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: int | None = None
    name: str
    email: str

users = {}
next_id = 1

@app.get("/users")
def list_users():
    return list(users.values())

@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="用户不存在")
    return users[user_id]

@app.post("/users", status_code=201)
def create_user(user: User):
    global next_id
    new_user = user.model_copy(update={"id": next_id})
    users[next_id] = new_user
    next_id += 1
    return new_user

@app.put("/users/{user_id}")
def update_user(user_id: int, user: User):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="用户不存在")
    users[user_id] = user.model_copy(update={"id": user_id})
    return users[user_id]

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="用户不存在")
    del users[user_id]
    return None
```

### 11.2 路径参数与查询参数

```python
from fastapi import FastAPI

app = FastAPI()

# 路径参数
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}

# 查询参数
@app.get("/users")
async def list_users(page: int = 1, size: int = 10):
    return {"page": page, "size": size}
```

- `/users/123` → `user_id=123`
- `/users?page=2&size=20` → `page=2, size=20`

### 11.3 请求体

```python
from pydantic import BaseModel

class CreateUserRequest(BaseModel):
    name: str
    email: str

@app.post("/users")
async def create_user(req: CreateUserRequest):
    return {"name": req.name, "email": req.email}
```

---

## 12. 动手实验

### 实验 1：用 curl 测试接口

启动一个 FastAPI 服务：

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
async def hello(name: str = "world"):
    return {"message": f"Hello, {name}!"}

@app.post("/echo")
async def echo(data: dict):
    return data
```

测试 GET 请求：

```bash
curl -X GET "http://localhost:8000/hello?name=FastAPI"
```

测试 POST 请求：

```bash
curl -X POST "http://localhost:8000/echo" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

### 实验 2：分析项目接口

1. 打开 `app/api/health.py`
2. 判断它用了什么 HTTP 方法
3. 它的 URL 是什么
4. 成功和失败时分别返回什么状态码
5. 响应结构是什么

### 实验 3：设计一套接口

假设要为一个图书馆系统设计 RESTful API，请设计以下接口：

- 图书的增删改查
- 作者的增删改查
- 查询某作者的所有图书
- 借阅图书
- 归还图书

写出每个接口的 HTTP 方法、URL 和请求/响应示例。

---

## 13. 学习检查清单

完成本讲义后，请确认你能回答以下问题：

- [ ] 什么是 RESTful API？它有什么特点？
- [ ] URL 设计应该注意什么？
- [ ] GET / POST / PUT / PATCH / DELETE 分别代表什么操作？
- [ ] 200 / 201 / 400 / 404 / 422 / 500 / 503 状态码的含义是什么？
- [ ] 什么是有状态？什么是无状态？为什么 REST 推荐无状态？
- [ ] 请求头和请求体有什么区别？
- [ ] 路径参数和查询参数有什么区别？

---

## 14. 下节课衔接

学完本课后，你将能够理解 FastAPI 项目中的 URL 设计、HTTP 方法和状态码选择，并能阅读项目中的各个 API 接口。

建议继续学习 **Python 异步编程**，为理解 FastAPI 的 `async def` 路由做准备。

---

*生成时间：2026/06/28*
*用途：AIAgent 项目实战课程前置知识补充*
