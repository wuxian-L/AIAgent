import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser,StrOutputParser
#1.模型Model
llm = ChatOpenAI(
    model = "qwen-max",
    base_url = "https://api.dashscope.com",
    api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxx",
)
#2.模板Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system","你是一个{role}，擅长{skill}。"),
    ("human","{question}"),
    ("placeholder", "history"),#占位符
])
#3.输出解析器Output Parser
parser =StrOutputParser()
chain = prompt | llm | parser
result = chain.invoke({
    "role":"运维专家",
    "skill":"运维",
    "question":"怎么定位具体是哪个服务？",
    "history":[
        ("human","服务器CPU过高怎么办？"),
        ("ai","请检查服务器的进程和负载情况。"),
    ]
})
print(result)