import os
from pathlib import Path
from langchain.chat_models import ChatOpenAI
KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = KNOWLEDGE_DIR / "config_5/config.py"

from config_5.config import settings
llm = ChatOpenAI(
    model = settings.dashscope_model,
    base_url = settings.dashscope_base_url,
    api_key = settings.dashscope_api_key,
    temperature = 0.7,
)
response = llm.invoke("请用一句话介绍FastAPI")
print(response)
print(response.content)
#返回值：AIMessage
'''
AIMessage 属于 LangChain 的 Message 类型，后续课程会详细讲。这里只需要知道：
.content：获取模型返回的文本内容
.response_metadata：包含 token 用量、模型名等元信息
.tool_calls：如果模型调用了工具，会在这里（Agent 课程讲）
'''
#同步和异步调用
response = llm.invoke("请用一句话介绍FastAPI")#同步调用
response = await llm.ainvoke("请用一句话介绍FastAPI")#异步调用
#流式输出
for chunk in llm.stream("请用一句话介绍FastAPI"):
    print(chunk.content, end="",flush=True)
#批量调用 多个独立输入，使用batch一次性调用,batch并发
inputs = ["请用一句话介绍FastAPI","请用一句话介绍LangChain"]
responses = llm.batch(inputs)
for response in responses:
    print(response.content)

