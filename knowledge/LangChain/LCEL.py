from langchain_openai import ChatOpenAI
import pydantic
llm = ChatOpenAI(
  model = "qwen-max",
  base_url = "https://api.deepseek.com/anthropic",
  api_key = "sk-fd9340c7f9154be2a0cd2ac979d33ecc",
  temperature=0.7,
)

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
#1.定义提示词模板
prompt = ChatPromptTemplate.from_messages([
    ("system","你是个{role},用{style}的风格回答问题"),
    ("human","{question}")
])
#2.输出解析器
parser = StrOutputParser()
#3.组合成链
chain = prompt | llm | parser 
#4.运行
result =  chain.invoke({
    "role":"Linux运维专家",
    "style":"简洁专业",
    "question":"服务器磁盘使用率达到95%,如何排查?"
})
print("="*60)
print("回答：")
print(result)
print("="*60)

