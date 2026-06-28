#同步代码
#目标：掌握 async / await 与 asyncio，为学习 FastAPI 和 Agent 开发打基础
import time
def make(name):
    time.sleep(2)
    return f"{name}"
print(make("炸鸡"))
print(make("可乐"))

#异步代码
import asyncio

async def make_async(name):
    await asyncio.sleep(2)
    return f"{name}"
async def main():
    task1 = asyncio.create_task(make_async("可乐"))
    task2 = asyncio.create_task(make_async("炸鸡"))

    result1 = await task1
    result2 = await task2
    print(result1)
    print(result2)
asyncio.run(main())
'''
协程 async def定义的函数
# 调用方式 1：错误
hello()  # 只会得到一个协程对象，不会执行，还会报 RuntimeWarning

# 调用方式 2：正确
asyncio.run(hello())

# 调用方式 3：在另一个 async 函数中调用
async def main():
    await hello()

asyncio.run(main())
'''

#事件循环
'''
事件循环是异步编程的心脏。它负责：

调度所有协程
当某个协程遇到 await 等待 IO 时，切换到其他协程执行
当 IO 完成后，唤醒对应的协程继续执行
你可以把事件循环想象成一个聪明的调度员，它让所有任务轮流使用 CPU，避免某个任务一直占着 CPU 干等。
'''
import asyncio
async def task(name,delay):
    print(f"任务{name}开始")
    await asyncio.sleep(delay)
    print(f"任务{name}完成")
async def main():
    await asyncio.gather(
        task("A",2),
        task("B",1),
        task("C",3)
    )
asyncio.run(main())

#Task任务
#协程的包装器，用于在事件循环中并发执行
#asyncio.create_task() 会立即把协程交给事件循环调度，不等它完成就继续执行后面的代码
async def say_after(delay,what):
    await asyncio.sleep(delay)
    print(what)
async def main():
    task1 = asyncio.create_task(say_after(1,"hello"))
    task2 = asyncio.create_task(say_after(2,"world"))
    await task1
    await task2
asyncio.run(main())

#.gather用于并发运行多个可等待对象,并等待它们全部完成
async def main():
    results = await asyncio.gather(
        fetch_user(1),
        fetch_user(2),
        fetch_user(3)
    )
    print(results)
asyncio.run(main())

#异步函数调用同步代码会堵塞整个事件循环
'''
正确做法：
1.如果库有异步版本，优先用异步版本
2.如果必须用同步代码，放到线程池中执行：
'''
# 将 blocking_io 外面包装一层
'''
理解有误
import asyncio
def blocking_io():
    import time
    time.sleep(3)
    return "done"
async def anotherstuff(name):
    await asyncio.sleep(2)
    print("异步事件完成")

async def main():
    #创建一个事件循环
    loop = asyncio.get_event_loop()
    
    result = await loop.run_in_executor(None,blocking_io)
    result1 = await loop.run_in_executor(None,anotherstuff)
    await print(result)
    await print(result1)
asyncio.run(main())
'''
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

#并发调用多个API
import asyncio
import httpx
async def check_service(url):
    async with httpx.AsyncClient() as client:
        resp = await client.get(url,timeout = 5)
        return {"url":url,"status":resp.status_code}
async def main():
    urls = [
        "http://localhost:9900/health",
        "http://localhost:8003/health",
        "http://localhost:8004/health"
    ]
    results = await asyncio.gather(*[check_service(url) for url in urls])
    ##### * 星号解包列表，传递的不是一个列表，而是一堆参数
    print(results)
asyncio.run(main())

# FastAPI中的异步路由
from fastapi import FastAPI
import httpx
app = FastAPI()
@app.get("/users/{user_id}")
async def get_user(user_id:int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://api.example.com/users/{user_id}")
        return resp.json()
