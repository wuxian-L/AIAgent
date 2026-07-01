# 旧版Legacy Chain 类与参数形式
# 新版LCEL Chain   组件与管道符 | 形式
# LCEL Chain 
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
import os
prompt = ChatPromptTemplate.from_messages([
    ("system","你是一个{role}，擅长{skill}。"),
    ("human","{question}"),
])
llm = ChatOpenAI(
    model = "qwen-max",
    base_url = "https://api.dashscope.com",
    api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxx",
    temperature = 0.7,
)
parser = StrOutputParser()
chain = prompt | llm | parser
result = chain.invoke({
    "role":"运维专家",
    "skill":"运维",
    "question":"怎么定位具体是哪个服务？",
})
print(result)

#invoke(dict)
result = chain.invoke({"role":"后端架构师","topic":"LangChain"})
print(result)
#ainvoke(dict)
import asyncio
async def main():
    result = await chain.ainvoke({"role":"后端架构师","topic":"LangChain"})
    print(result)
asyncio.run(main())
from fastapi import FastAPI
from langchain_core.runnable import RunnableSequence
app = FastAPI()
@app.post("/api/chat")
async def chat(req:ChatRequest):
    result = await chain.ainvoke({
        "role":req.role,
        "skill":req.skill,
        "question":req.question
    })
    return {"result":result}
#stream
for chunk in chain.stream({"role":"后端架构师","topic":"LangChain"}):
    print(chunk,end="",flush=True)
#astream
async def main():
    async for chunk in chain.astream({"role":"后端架构师","topic":"LangChain"}):
        print(chunk,end="",flush=True)
#batch 并发调用
inputs = [
    {"role":"后端架构师","topic":"LangChain"},
    {"role":"运维专家","topic":"Milvus"},
    {"role":"产品经理","topic":"ARG"}
]
results = chain.batch(inputs)
for result in results:
    print(result)
#abatch

#查看 Chain 的输入输出 Schema
print(chain.get_input_schema().schema())
print(chain.get_output_schema().schema())

#调试Chain
#1.全局调试set_debug(True)开启后，LangChain 会打印每个 Runnable 的输入、输出和耗时
from langchain.globals import set_debug
set_debug(True)
chain.invoke({...})
#2.单独测试每个组件 返回值会包含相关信息
#测试prompt
messages = prompt.invoke({"role":"专家","topic":"LangChain"})
print(messages)
#测试llm
response = llm.invoke(messages)
print(response.content)
#测试parser
text = parser.ivoke(response)
print(text)
#3.查看链的图结构
chain.get_graph.print_ascii()


