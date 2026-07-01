# 启动 FastAPI 服务并完成实验 1

> 对应讲义：`Tutorial\RESTfulAPI前置讲义.md` 第 12 节「动手实验 · 实验 1」  
> 实验目标：在 `knowledge\RESTfulAPI\lab.py` 中启动一个 FastAPI 服务，并用 curl 测试 GET 和 POST 接口。

---

## 1. 前置依赖

实验需要安装 `fastapi` 和 `uvicorn`：

```bash
pip install fastapi uvicorn
```

> `fastapi` 用于编写接口，`uvicorn` 是运行 FastAPI 的 ASGI 服务器。

---

## 2. 实验代码

`knowledge\RESTfulAPI\lab.py` 中应包含以下代码：

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

说明：

- `@app.get("/hello")` 定义了一个 GET 接口，查询参数 `name` 默认值为 `"world"`。
- `@app.post("/echo")` 定义了一个 POST 接口，接收任意 JSON 对象并原样返回。

---

## 3. 启动服务

在项目根目录 `C:\Users\10497\Documents\AIAgent` 下执行：

```bash
uvicorn knowledge.RESTfulAPI.lab:app --host 127.0.0.1 --port 8000
```

启动成功后会看到类似输出：

```
INFO:     Started server process [7028]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

> 提示：`knowledge.RESTfulAPI.lab:app` 表示「模块路径 `knowledge.RESTfulAPI.lab` 中的 `app` 对象」。  
> Windows 路径分隔符既可以用 `.`（Python 包路径），也可以用 `/`。

---

## 4. 用 curl 测试接口

### 4.1 测试 GET 请求

```bash
curl -X GET "http://localhost:8000/hello?name=FastAPI"
```

预期响应：

```json
{"message":"Hello, FastAPI!"}
```

### 4.2 测试 POST 请求

```bash
curl -X POST "http://localhost:8000/echo" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

预期响应：

```json
{"key":"value"}
```

### 4.3 在 PowerShell 中测试

PowerShell 里的 `curl` 是 `Invoke-WebRequest` 的别名，**不支持 `-X`、`-H`、`-d` 这些参数**，会报错：

```
Invoke-WebRequest : 找不到与参数名称“X”匹配的参数。
```

请改用以下任一方式：

**方式 A：使用 `curl.exe`（推荐，命令和讲义一致）**

```powershell
curl.exe -X GET "http://localhost:8000/hello?name=FastAPI"
```

```powershell
curl.exe -X POST "http://localhost:8000/echo" `
  -H "Content-Type: application/json" `
  -d '{"key": "value"}'
```

**方式 B：使用 PowerShell 原生的 `Invoke-RestMethod`**

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/hello?name=FastAPI" -Method GET
```

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/echo" -Method POST `
  -ContentType "application/json" `
  -Body '{"key": "value"}'
```

**方式 C：换用 Git Bash 或 CMD**

在 Git Bash 或 Windows CMD 中，直接执行讲义里的 curl 命令即可。

---

## 5. 停止服务

在运行服务的终端窗口按 `Ctrl + C` 即可停止 uvicorn 服务器。

---

## 6. 常见问题

| 问题 | 原因 | 解决方法 |
|------|------|----------|
| `ModuleNotFoundError: No module named 'fastapi'` | 未安装依赖 | 执行 `pip install fastapi uvicorn` |
| `Error: [WinError 10048] 端口被占用` | 8000 端口已有其他程序使用 | 换端口启动，如 `--port 8001` |
| `ModuleNotFoundError: No module named 'knowledge'` | 未在项目根目录执行 | 切换到 `AIAgent` 目录再启动 |
| PowerShell 中 `curl -X` 报错「找不到与参数名称“X”匹配的参数」 | PowerShell 的 `curl` 是 `Invoke-WebRequest` 别名 | 改用 `curl.exe` 或 `Invoke-RestMethod`，详见 4.3 节 |

---

## 7. 下一步

完成实验 1 后，可以继续完成讲义中的：

- **实验 2**：分析项目中的 `app/api/health.py` 接口。
- **实验 3**：为图书馆系统设计一套 RESTful API。

---

*生成时间：2026/06/29*  
*用途：AIAgent 项目实战课程前置知识补充*
