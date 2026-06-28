# AIAgent 前置知识补充讲义 · HTTP 协议

> 本讲义为 AIAgent 项目实战课程的前置知识补充
> 目标：系统回顾 HTTP 协议，补齐知识体系，学会在 Python 中使用 httpx 进行 HTTP 请求
> 适用对象：有 Java 背景、需要查漏补缺的同学
> 建议学习时长：90-120 分钟（理论 + 实验）

---

## 1. HTTP 协议是什么

HTTP（HyperText Transfer Protocol，超文本传输协议）是互联网上应用最广泛的一种网络协议。它是**客户端和服务器之间通信的规则**。

你可以把 HTTP 想象成"寄快递"：

- **客户端**（浏览器、App、Python 脚本）= 寄件人
- **服务器**（网站后端、API 服务）= 收件人
- **HTTP 请求** = 你填写的快递单和包裹
- **HTTP 响应** = 对方寄回的快递

我们每天访问网页、调用接口、发送消息，底层都是 HTTP 协议在工作。

---

## 2. HTTP 的特点

| 特点 | 说明 |
|------|------|
| **基于请求-响应模型** | 客户端发送请求，服务器返回响应，一一对应 |
| **无状态** | 服务器默认不记住客户端之前做了什么 |
| **无连接** | HTTP/1.0 默认每次请求后断开；HTTP/1.1 支持长连接（Keep-Alive） |
| **灵活** | 可以传输任意类型的数据（文本、图片、JSON、视频等） |
| **明文传输** | HTTP 不加密，HTTPS 才是加密的 |

---

## 3. HTTP 工作过程

一次完整的 HTTP 通信包含以下步骤：

```
1. 客户端与服务器建立 TCP 连接
2. 客户端发送 HTTP 请求
3. 服务器处理请求
4. 服务器返回 HTTP 响应
5. 关闭连接（或保持连接复用）
```

用生活场景类比：

```
你（客户端） → 打电话到餐厅（建立连接）
          → "我要一份宫保鸡丁外卖"（发送请求）
餐厅（服务器） → 做菜（处理请求）
            → "好的，马上送到"（返回响应）
          → 挂断电话（关闭连接）
```

---

## 4. HTTP 请求报文

HTTP 请求报文由三部分组成：

```
请求行（Request Line）
请求头（Request Headers）
请求体（Request Body，可选）
```

### 4.1 请求行

请求行包含三个部分：

```
方法 URL HTTP版本
```

示例：

```http
GET /api/users/1 HTTP/1.1
```

- `GET`：HTTP 方法
- `/api/users/1`：请求的资源路径
- `HTTP/1.1`：HTTP 协议版本

### 4.2 请求头

请求头是一组键值对，用来告诉服务器更多信息。

```http
GET /api/users/1 HTTP/1.1
Host: api.example.com
User-Agent: Mozilla/5.0
Accept: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json
```

常见请求头：

| Header | 说明 | 类比 |
|--------|------|------|
| `Host` | 目标服务器域名 | 快递收件地址 |
| `User-Agent` | 客户端身份标识 | 寄件人姓名 |
| `Accept` | 希望接收的数据格式 | 希望收到纸质文件还是电子版 |
| `Content-Type` | 请求体数据格式 | 包裹里是什么东西 |
| `Authorization` | 认证信息 | 身份证/门禁卡 |
| `Content-Length` | 请求体长度 | 包裹重量 |
| `Cookie` | 服务器之前设置的 Cookie | 会员卡号 |

### 4.3 请求体

请求体是客户端发送给服务器的数据。只有 POST、PUT、PATCH 等请求通常才有请求体。

```http
POST /api/users HTTP/1.1
Host: api.example.com
Content-Type: application/json
Content-Length: 52

{
    "name": "张三",
    "email": "zhangsan@example.com"
}
```

空行之后就是请求体。

---

## 5. HTTP 响应报文

HTTP 响应报文也由三部分组成：

```
状态行（Status Line）
响应头（Response Headers）
响应体（Response Body，可选）
```

### 5.1 状态行

状态行包含三个部分：

```
HTTP版本 状态码 状态描述
```

示例：

```http
HTTP/1.1 200 OK
```

### 5.2 响应头

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 78
Server: nginx
Set-Cookie: session_id=abc123; Path=/; HttpOnly
```

常见响应头：

| Header | 说明 |
|--------|------|
| `Content-Type` | 响应体格式 |
| `Content-Length` | 响应体长度 |
| `Server` | 服务器软件信息 |
| `Set-Cookie` | 让客户端保存 Cookie |
| `Location` | 重定向目标地址 |
| `Cache-Control` | 缓存控制策略 |

### 5.3 响应体

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "id": 1,
    "name": "张三",
    "email": "zhangsan@example.com"
}
```

---

## 6. HTTP 方法

HTTP 方法定义了对资源的操作类型。

| 方法 | 含义 | 是否幂等 | 是否有请求体 |
|------|------|---------|-------------|
| `GET` | 获取资源 | 是 | 否 |
| `POST` | 创建/提交资源 | 否 | 是 |
| `PUT` | 全量更新资源 | 是 | 是 |
| `PATCH` | 部分更新资源 | 否 | 是 |
| `DELETE` | 删除资源 | 是 | 否 |
| `HEAD` | 获取响应头（不返回体） | 是 | 否 |
| `OPTIONS` | 查询支持的请求方法 | 是 | 否 |

### 6.1 GET

用于获取资源，参数放在 URL 中。

```http
GET /api/users?page=1&size=10 HTTP/1.1
Host: api.example.com
```

### 6.2 POST

用于创建资源或提交数据，数据放在请求体中。

```http
POST /api/users HTTP/1.1
Host: api.example.com
Content-Type: application/json

{"name":"李四","email":"lisi@example.com"}
```

### 6.3 PUT

用于完整替换资源。

```http
PUT /api/users/1 HTTP/1.1
Host: api.example.com
Content-Type: application/json

{"name":"张三三","email":"zhangsan@example.com"}
```

### 6.4 PATCH

用于部分更新资源。

```http
PATCH /api/users/1 HTTP/1.1
Host: api.example.com
Content-Type: application/json

{"name":"张三三"}
```

### 6.5 DELETE

用于删除资源。

```http
DELETE /api/users/1 HTTP/1.1
Host: api.example.com
```

---

## 7. HTTP 状态码

状态码用于表示请求处理的结果，由三位数字组成。

### 7.1 状态码分类

| 范围 | 类别 | 说明 |
|------|------|------|
| 1xx | 信息响应 | 请求已接收，继续处理 |
| 2xx | 成功 | 请求成功处理 |
| 3xx | 重定向 | 需要进一步操作才能完成请求 |
| 4xx | 客户端错误 | 请求有问题 |
| 5xx | 服务器错误 | 服务器处理失败 |

### 7.2 常见状态码

#### 2xx 成功

| 状态码 | 含义 | 场景 |
|--------|------|------|
| 200 | OK | 通用成功 |
| 201 | Created | 资源创建成功 |
| 204 | No Content | 成功但无返回体 |

#### 3xx 重定向

| 状态码 | 含义 | 场景 |
|--------|------|------|
| 301 | Moved Permanently | 永久重定向 |
| 302 | Found | 临时重定向 |
| 304 | Not Modified | 资源未修改，使用缓存 |

#### 4xx 客户端错误

| 状态码 | 含义 | 场景 |
|--------|------|------|
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证 |
| 403 | Forbidden | 无权限 |
| 404 | Not Found | 资源不存在 |
| 405 | Method Not Allowed | 请求方法不允许 |
| 408 | Request Timeout | 请求超时 |
| 422 | Unprocessable Entity | 请求格式正确但语义错误 |
| 429 | Too Many Requests | 请求过于频繁 |

#### 5xx 服务器错误

| 状态码 | 含义 | 场景 |
|--------|------|------|
| 500 | Internal Server Error | 服务器内部错误 |
| 502 | Bad Gateway | 网关错误 |
| 503 | Service Unavailable | 服务不可用 |
| 504 | Gateway Timeout | 网关超时 |

---

## 8. URL 详解

URL（Uniform Resource Locator，统一资源定位符）是互联网上资源的地址。

```
https://www.example.com:8080/api/users?id=1&page=2#section1
```

组成部分：

| 部分 | 示例 | 说明 |
|------|------|------|
| 协议 | `https://` | 通信协议 |
| 域名 | `www.example.com` | 服务器地址 |
| 端口 | `:8080` | 服务端口，HTTP 默认 80，HTTPS 默认 443 |
| 路径 | `/api/users` | 资源路径 |
| 查询参数 | `?id=1&page=2` | 附加参数 |
| 锚点 | `#section1` | 页面内定位，不发送到服务器 |

### 8.1 查询参数编码

URL 中有些字符有特殊含义，需要编码：

| 原始字符 | URL 编码 |
|---------|---------|
| 空格 | `%20` 或 `+` |
| `&` | `%26` |
| `=` | `%3D` |
| 中文字符 | 如 `中` → `%E4%B8%AD` |

---

## 9. Cookie、Session、Token

HTTP 是无状态的，但很多时候我们需要识别用户身份。常见的解决方案有三种。

### 9.1 Cookie

Cookie 是服务器让浏览器保存的一小段文本，之后每次请求浏览器都会自动带上。

流程：

```
1. 客户端第一次访问服务器
2. 服务器在响应头中设置 Set-Cookie: user_id=123
3. 浏览器保存 Cookie
4. 以后客户端每次请求都自动带上 Cookie: user_id=123
```

### 9.2 Session

Session 是服务器端保存的用户状态。服务器给客户端一个 Session ID（通常通过 Cookie），客户端每次带上 Session ID，服务器根据 ID 查找对应的用户状态。

```
客户端 ←→ Cookie: session_id=xxx ←→ 服务器内存/Redis 中的 Session 数据
```

### 9.3 Token

Token 是服务器签发的一串加密字符串，客户端每次请求都带上。服务器通过验证 Token 来识别用户身份。

常见 Token 类型：

- JWT（JSON Web Token）
- API Key
- OAuth Access Token

```http
GET /api/user/profile HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### 9.4 三者对比

| 方案 | 数据存储位置 | 优点 | 缺点 |
|------|------------|------|------|
| Cookie | 浏览器 | 自动携带，使用简单 | 容量小，有安全风险 |
| Session | 服务器 | 安全性高 | 服务器需要维护状态，不易扩展 |
| Token | 客户端 | 无状态，易扩展 | Token 管理复杂，过期处理麻烦 |

---

## 10. HTTP vs HTTPS

| 对比项 | HTTP | HTTPS |
|--------|------|-------|
| 安全性 | 明文传输，不安全 | SSL/TLS 加密，安全 |
| 默认端口 | 80 | 443 |
| 性能 | 较快 | 有加密开销，但可接受 |
| 证书 | 不需要 | 需要 SSL 证书 |
| URL 前缀 | `http://` | `https://` |

HTTPS = HTTP + SSL/TLS。它在传输层对数据进行加密，防止中间人窃听和篡改。

---

## 11. Python 中的 HTTP 请求：httpx

### 11.1 为什么选择 httpx

Python 中常用的 HTTP 库有：

| 库 | 特点 |
|---|------|
| `requests` | 同步、易用、生态成熟 |
| `httpx` | 同时支持同步和异步、API 与 requests 类似 |
| `aiohttp` | 纯异步、性能高 |

在 FastAPI 项目中，推荐使用 **httpx**，因为它：

- 同时支持同步和异步客户端
- API 设计与 requests 相似，容易上手
- 与 asyncio 配合良好

### 11.2 安装

```bash
pip install httpx
```

### 11.3 同步请求

```python
import httpx

# GET 请求
response = httpx.get("https://api.github.com")
print(response.status_code)  # 200
print(response.headers["Content-Type"])  # application/json
print(response.json())  # 解析 JSON 响应

# POST 请求
response = httpx.post(
    "https://httpbin.org/post",
    json={"name": "张三", "age": 25}
)
print(response.json())
```

### 11.4 异步请求

```python
import asyncio
import httpx

async def fetch():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.github.com")
        print(response.status_code)
        print(response.json())

asyncio.run(fetch())
```

关键点：

- 使用 `AsyncClient()` 创建异步客户端
- 用 `await` 等待请求完成
- 使用 `async with` 自动管理资源

### 11.5 自定义 Headers 和参数

```python
import httpx

headers = {
    "User-Agent": "MyApp/1.0",
    "Authorization": "Bearer my_token"
}

params = {
    "page": 1,
    "size": 10
}

response = httpx.get(
    "https://api.example.com/users",
    headers=headers,
    params=params
)
print(response.url)  # 会自动拼接参数
print(response.json())
```

### 11.6 上传文件

```python
import httpx

with open("document.pdf", "rb") as f:
    files = {"file": ("document.pdf", f, "application/pdf")}
    response = httpx.post("https://api.example.com/upload", files=files)
    print(response.status_code)
```

### 11.7 超时设置

```python
import httpx

try:
    response = httpx.get("https://api.example.com/slow", timeout=5.0)
except httpx.TimeoutException:
    print("请求超时")
```

### 11.8 与 Java 的 HttpClient 对比

| 场景 | Python (httpx) | Java (HttpClient) |
|------|---------------|-------------------|
| 同步 GET | `httpx.get(url)` | `HttpClient.newHttpClient().send(...)` |
| 异步 GET | `await client.get(url)` | `client.sendAsync(...)` |
| 设置 Header | `headers={...}` | `.header("Key", "Value")` |
| JSON 请求 | `json={...}` | `HttpRequest.BodyPublishers.ofString(json)` |
| 超时 | `timeout=5.0` | `.timeout(Duration.ofSeconds(5))` |

---

## 12. 项目中的应用

### 12.1 项目接口调用示例

假设服务运行在 `http://localhost:9900`，我们可以用 httpx 测试：

```python
import httpx

# 健康检查
response = httpx.get("http://localhost:9900/health")
print(response.status_code)
print(response.json())

# 对话请求
response = httpx.post(
    "http://localhost:9900/api/chat",
    json={
        "Id": "session-123",
        "Question": "什么是向量数据库？"
    }
)
print(response.json())
```

### 12.2 FastAPI 如何接收 HTTP 请求

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    id: str
    question: str

@app.post("/api/chat")
async def chat(req: ChatRequest):
    return {
        "code": 200,
        "message": "success",
        "data": {"answer": f"你问的是：{req.question}"}
    }
```

FastAPI 会自动：

- 解析请求体 JSON
- 校验字段类型
- 生成响应 JSON
- 设置正确的 `Content-Type: application/json`

---

## 13. 动手实验

### 实验 1：观察真实 HTTP 请求

用浏览器访问 `https://httpbin.org/get`，然后按 F12 打开开发者工具，观察 Network 标签中的请求头和响应头。

### 实验 2：用 httpx 发送各种请求

```python
import httpx

# GET 带参数
r = httpx.get("https://httpbin.org/get", params={"key": "value"})
print(r.status_code, r.json())

# POST JSON
r = httpx.post("https://httpbin.org/post", json={"name": "张三"})
print(r.json())

# 自定义 Header
r = httpx.get("https://httpbin.org/headers", headers={"X-Custom": "hello"})
print(r.json())
```

### 实验 3：测试项目接口

启动 AIAgent 项目后，用 httpx 调用：

```python
import httpx

# 健康检查
r = httpx.get("http://localhost:9900/health")
print(r.status_code)
print(r.json())
```

### 实验 4：用 curl 构造请求

```bash
# GET
curl -X GET "https://httpbin.org/get" -H "Accept: application/json"

# POST JSON
curl -X POST "https://httpbin.org/post" \
  -H "Content-Type: application/json" \
  -d '{"name":"张三"}'

# 查看响应头
curl -I "https://httpbin.org/get"
```

---

## 14. 学习检查清单

完成本讲义后，请确认你能回答以下问题：

- [ ] HTTP 请求报文由哪三部分组成？
- [ ] 常见的 HTTP 方法有哪些？分别对应什么操作？
- [ ] GET 和 POST 的主要区别是什么？
- [ ] 200、201、400、401、403、404、500、503 分别代表什么？
- [ ] URL 由哪些部分组成？
- [ ] Cookie、Session、Token 的区别是什么？
- [ ] HTTP 和 HTTPS 的区别是什么？
- [ ] 如何在 Python 中用 httpx 发送同步和异步请求？
- [ ] FastAPI 如何接收和返回 JSON 数据？

---

## 15. 下节课衔接

学完 HTTP 协议后，建议继续学习 **JSON 数据格式**，因为 API 的请求和响应体几乎都是 JSON。

---

*生成时间：2026/06/28*
*用途：AIAgent 项目实战课程前置知识补充*
