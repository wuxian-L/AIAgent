# AIAgent 前置知识补充讲义 · Python 异步编程

> 本讲义为 AIAgent 项目实战课程的前置知识补充
> 目标：掌握 `async` / `await` 与 `asyncio`，为学习 FastAPI 和 Agent 开发打基础
> 建议学习时长：60-90 分钟（理论 + 实验）

---

## 1. 为什么要学异步编程

在进入 FastAPI 之前，你必须先理解 Python 的异步编程。因为：

1. **FastAPI 原生支持异步**：它的路由函数可以直接写成 `async def`。
2. **Agent 项目大量 IO 操作**：调用大模型 API、查询 Milvus 向量库、调用 MCP 工具、读写文件，这些都是网络或磁盘 IO。
3. **异步能显著提升并发能力**：同样的服务器资源，异步模式能同时处理更多请求。

如果你只会写同步代码，面对 FastAPI 和 LangChain 的异步接口时会非常吃力。

---

## 2. 同步 vs 异步：一个生活例子

### 2.1 同步：排队买咖啡

你走进咖啡店，对服务员说：

1. "我要一杯美式" → 服务员开始制作
2. 你站着等 3 分钟 → 咖啡做好
3. 你拿到咖啡，才去做下一件事

这就是**同步**：你必须等待当前任务完成，才能继续下一个任务。

### 2.2 异步：扫码点单

你扫码点单后：

1. 下单成功，拿到取餐号
2. 你坐下来刷手机（不站着等）
3. 咖啡做好了，服务员叫号，你去取

这就是**异步**：你不需要阻塞在当前任务上，等待期间可以做其他事情。

### 2.3 程序中的同步与异步

```python
# 同步代码：按顺序执行，等待每个操作完成
import time

def make_coffee(name):
    time.sleep(2)  # 模拟做咖啡需要 2 秒
    return f"{name} 做好了"

print(make_coffee("美式"))
print(make_coffee("拿铁"))
# 总共耗时 4 秒
```

```python
# 异步代码：不需要等待，可以并发执行
import asyncio

async def make_coffee(name):
    await asyncio.sleep(2)  # 模拟异步等待
    return f"{name} 做好了"

async def main():
    # 同时开始做两杯咖啡
    task1 = asyncio.create_task(make_coffee("美式"))
    task2 = asyncio.create_task(make_coffee("拿铁"))
    
    result1 = await task1
    result2 = await task2
    print(result1)
    print(result2)
    # 总共耗时约 2 秒

asyncio.run(main())
```

---

## 3. 核心概念

### 3.1 协程（Coroutine）

用 `async def` 定义的函数就是**协程**。调用它不会立即执行，而是返回一个协程对象。

```python
async def hello():
    print("Hello")

# 调用方式 1：错误
hello()  # 只会得到一个协程对象，不会执行，还会报 RuntimeWarning

# 调用方式 2：正确
asyncio.run(hello())

# 调用方式 3：在另一个 async 函数中调用
async def main():
    await hello()

asyncio.run(main())
```

### 3.2 async / await 关键字

| 关键字 | 含义 |
|--------|------|
| `async` | 定义一个协程函数或异步上下文管理器、异步迭代器 |
| `await` | 等待一个可等待对象（协程、Task、Future）完成，同时让出 CPU |

**规则：**

- `await` 只能在 `async def` 函数内部使用
- `await` 后面的对象必须是 "可等待的"（awaitable）

### 3.3 事件循环（Event Loop）

事件循环是异步编程的心脏。它负责：

- 调度所有协程
- 当某个协程遇到 `await` 等待 IO 时，切换到其他协程执行
- 当 IO 完成后，唤醒对应的协程继续执行

你可以把事件循环想象成一个聪明的调度员，它让所有任务轮流使用 CPU，避免某个任务一直占着 CPU 干等。

```python
import asyncio

async def task(name, delay):
    print(f"任务 {name} 开始")
    await asyncio.sleep(delay)  # 假装在做 IO 操作
    print(f"任务 {name} 完成")

async def main():
    await asyncio.gather(
        task("A", 2),
        task("B", 1),
        task("C", 3)
    )

asyncio.run(main())
```

输出顺序：

```
任务 A 开始
任务 B 开始
任务 C 开始
任务 B 完成  # 1 秒后
任务 A 完成  # 2 秒后
任务 C 完成  # 3 秒后
```

三个任务总共耗时约 3 秒，而不是 6 秒。

### 3.4 Task（任务）

Task 是协程的包装器，用于在事件循环中并发执行。

```python
async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)

async def main():
    # 创建任务
    task1 = asyncio.create_task(say_after(1, "hello"))
    task2 = asyncio.create_task(say_after(2, "world"))
    
    # 等待两个任务都完成
    await task1
    await task2

asyncio.run(main())
```

`asyncio.create_task()` 会立即把协程交给事件循环调度，不等它完成就继续执行后面的代码。

### 3.5 asyncio.gather

`gather` 用于并发运行多个可等待对象，并等待它们全部完成：

```python
async def main():
    results = await asyncio.gather(
        fetch_user(1),
        fetch_user(2),
        fetch_user(3)
    )
    print(results)  # [user1, user2, user3]

asyncio.run(main())
```

### 3.6 asyncio.run

`asyncio.run(coro)` 是启动异步程序的入口：

- 创建新的事件循环
- 运行传入的协程
- 协程完成后关闭事件循环

**注意：** 一个程序中通常只调用一次 `asyncio.run()`，一般在 `if __name__ == "__main__":` 中。

---

## 4. 阻塞 vs 非阻塞

### 4.1 阻塞操作

阻塞操作会让整个线程停下来等待，期间什么也干不了：

- `time.sleep(3)`
- `requests.get(url)`（同步 HTTP 请求）
- 同步文件读写
- 同步数据库查询

### 4.2 非阻塞操作

非阻塞操作会让出 CPU，让事件循环去执行其他任务：

- `await asyncio.sleep(3)`
- `await httpx.AsyncClient().get(url)`（异步 HTTP 请求）
- 异步文件读写（`aiofiles`）
- 异步数据库查询

### 4.3 在异步函数中调用同步代码会怎样

```python
async def bad_example():
    time.sleep(3)  # 错误！这会阻塞整个事件循环
    return "done"
```

如果你在 `async def` 函数里调用同步阻塞代码，整个事件循环都会被卡住，其他请求也无法处理。

**正确做法：**

1. 如果库有异步版本，优先用异步版本
2. 如果必须用同步代码，放到线程池中执行：

```python
import asyncio

def blocking_io():
    import time
    time.sleep(3)
    return "done"

async def main():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, blocking_io)
    print(result)

asyncio.run(main())
```

---

## 5. 实际应用场景

### 5.1 并发调用多个 API

假设你要同时查询三个服务的健康状态：

```python
import asyncio
import httpx

async def check_service(url):
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=5)
        return {"url": url, "status": resp.status_code}

async def main():
    urls = [
        "http://localhost:9900/health",
        "http://localhost:8003/health",
        "http://localhost:8004/health"
    ]
    results = await asyncio.gather(*[check_service(url) for url in urls])
    print(results)

asyncio.run(main())
```

三个请求同时发出，总耗时接近最慢的那个请求，而不是三者之和。

### 5.2 FastAPI 中的异步路由

```python
from fastapi import FastAPI
import httpx

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://api.example.com/users/{user_id}")
        return resp.json()
```

当这个接口被调用时：

1. 等待外部 API 响应期间，FastAPI 可以处理其他请求
2. 响应回来后，继续执行当前函数

---

## 6. 在我们项目中的应用

在 AIAgent 项目中，异步编程无处不在：

| 场景 | 为什么需要异步 |
|------|---------------|
| 调用 DashScope 大模型 API | 网络 IO，等待响应时间长 |
| 查询 Milvus 向量库 | 网络 IO |
| 调用 MCP 工具 | 网络 IO |
| 流式输出 `/api/chat_stream` | 需要边生成边发送 |
| 同时处理多个用户请求 | 提升并发能力 |

看一个简化示例：

```python
@app.post("/api/chat")
async def chat(request: ChatRequest):
    # 这里可能会调用 LLM、查询向量库、调用工具
    response = await rag_agent_service.chat(request.id, request.question)
    return response
```

如果不用 `async`，一个用户提问时，服务器就被阻塞住，其他用户只能排队等待。

---

## 7. 常见错误与误区

### 错误 1：在同步函数中使用 await

```python
def foo():
    await asyncio.sleep(1)  # SyntaxError
```

**解决：** 把函数改成 `async def`。

### 错误 2：忘记 await

```python
async def main():
    result = asyncio.sleep(1)  # 没有 await，不会等待
    print("done")
```

**解决：** 对协程使用 `await` 或 `create_task`。

### 错误 3：用 async 但里面全是同步代码

```python
async def slow():
    time.sleep(5)  # 阻塞了事件循环
```

**解决：** 用 `await asyncio.sleep(5)` 或线程池。

### 错误 4：多次调用 asyncio.run()

```python
asyncio.run(main())
asyncio.run(another())  # 可能报错
```

**解决：** 一个程序通常只调用一次 `asyncio.run()`。

### 错误 5：混淆并发与并行

- **并发（Concurrency）**：多个任务交替执行，看起来同时进行（单核 CPU 也可以）
- **并行（Parallelism）**：多个任务真正同时进行（需要多核 CPU）

异步主要解决的是**并发**，不是并行。但它已经能极大提升 IO 密集型程序的性能。

---

## 8. 动手实验

### 实验 1：基础 async / await

```python
import asyncio

async def count():
    print("1")
    await asyncio.sleep(1)
    print("2")

async def main():
    await asyncio.gather(count(), count(), count())

asyncio.run(main())
```

预期输出：

```
1
1
1
2
2
2
```

三个 `count` 几乎同时开始，每个等待 1 秒后同时结束。

### 实验 2：对比同步与异步耗时

同步版本：

```python
import time

def task(n):
    time.sleep(1)
    print(f"任务 {n} 完成")

start = time.time()
for i in range(5):
    task(i)
print(f"同步总耗时：{time.time() - start:.2f} 秒")
```

异步版本：

```python
import asyncio
import time

async def task(n):
    await asyncio.sleep(1)
    print(f"任务 {n} 完成")

async def main():
    await asyncio.gather(*[task(i) for i in range(5)])

start = time.time()
asyncio.run(main())
print(f"异步总耗时：{time.time() - start:.2f} 秒")
```

### 实验 3：并发请求多个 URL

```python
import asyncio
import httpx

async def fetch(url):
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        return len(resp.text)

async def main():
    urls = [
        "https://www.example.com",
        "https://www.baidu.com",
        "https://www.bing.com"
    ]
    results = await asyncio.gather(*[fetch(url) for url in urls])
    print(results)

asyncio.run(main())
```

---

## 9. 学习检查清单

完成本讲义后，请确认你能回答以下问题：

- [ ] 什么是协程？如何定义和调用？
- [ ] `async` 和 `await` 分别是什么意思？
- [ ] 事件循环的作用是什么？
- [ ] `asyncio.create_task()` 和 `asyncio.gather()` 有什么区别？
- [ ] 阻塞操作和非阻塞操作有什么区别？
- [ ] 为什么在 `async def` 函数中不能用 `time.sleep()`？
- [ ] 异步编程主要解决什么问题？

---

## 10. 下节课衔接

学完本课后，你将能够理解 FastAPI 的 `async def` 路由函数，并明白为什么 Agent 项目要大量依赖异步编程。

下一节建议继续学习 **RESTful API 基础**，理解 HTTP 方法和接口设计规范。

---

*生成时间：2026/06/28*
*用途：AIAgent 项目实战课程前置知识补充*
