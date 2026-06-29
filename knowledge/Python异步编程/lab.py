#基础async/await
'''
import asyncio
async def count():
    print("1")
    await asyncio.sleep(1)
    print("2")

async def main():
    await asyncio.gather(count(),count(),count())
asyncio.run(main())
'''
#对比同步和异步耗时
'''
import time
def task(n):
    time.sleep(1)
    print(f"任务{n}完成")
start = time.time()
for i in range(5):
    task(i)
print(f"同步总耗时：{time.time() - start:.2f}秒")
'''
'''
import asyncio
import time
async def task(n):
    await asyncio.sleep(1)
    print(f"任务{n}完成")
async def main():
    await asyncio.gather(*[task(i) for i in range(5)])
start = time.time()
asyncio.run(main())
print(f"异步总耗时：{time.time() - start:.3f}秒")
'''
#并发请求多个URL
async def fetch(client, url):
    resp = await client.get(url)
    return len(resp.text)

async def main():
    urls = [
        "https://www.example.com",
        "https://www.baidu.com",
        "https://www.bing.com"
    ]
    #同一个client，连接复用
    async with httpx.AsyncClient() as client:
        tasks = [fetch(client, url) for url in urls]
        results = await asyncio.gather(*tasks)
    print(results)
asyncio.run(main())



