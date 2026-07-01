from langchain_cores.prompts import PromptTemplate
#字符串模板
template = PromptTemplate(
    "请用{style}风格写一首关于{topic}的诗，要求{requirements}。",
)
prompt_value = template.invoke({
    "style": "古风",
    "topic": "春天",
    "requirements": "每句诗都要押韵",
})#.invoke()方法,渲染提示词 会返回一个PromptValue对象，包含了最终的prompt文本和变量值
print(prompt_value.to_string())
#消息模板
from langchain_cores.prompt import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
template = ChatPromptTemplate.from_messages([
    ("system","你是一个{role}，擅长{skill}。"),
    ("human","请用一句话介绍{topic}。"),
])
#返回一个List[BaseMessage]对象
messages = template.invoke({
    "role": "诗人",
    "skill": "写诗",
    "topic": "春天",
})
print(messages)
'''
输出：
[SystemMessage(content='你是一个诗人，擅长写诗。', additional_kwargs={}), 
HumanMessage(content='请用一句话介绍春天。', additional_kwargs={})]
'''
#模板中插入历史消息 ("placeholder","history")占位符
template = ChatPromptTemplate.from_messages([
    ("system","你是一个{role}，擅长{skill}。"),
    ("human","{question}"),
    ("placeholder", "history"),#占位符
])
messages = template.invoke({
    "role":"运维专家",
    "skill":"运维",
    "question":"怎么定位具体是哪个服务？",
    "history":[
        ("human","服务器CPU过高怎么办？"),
        ("ai","请检查服务器的进程和负载情况。"),
    ]
})

#Output Parser:输出解析器
#大模型返回的是文本，程序需要将文本解析为结构化数据，Output Parser就是用来做这个事情的
'''
{
    "root_cause":"服务器CPU过高",
    "recommendations":["扩容连接池","优化SQL"]
}
'''
#StrOutputParser:将文本解析为字符串
from langchain_core.output_parsers import StrOutputParser
parser = StrOutputParser()
result = parser.invoke("这是一个字符串")
print(result)

#PydanticOutputParser:结构化解析器
from pydantic import BaseModel,Field
#1.定义Pydantic模型
class Diagnosis(BaseModel):
    root_cause:str = Field(...,description="根因")
    recommendations:list[str] = Field(...,description="建议")
#2.创建解析器并 获取 **格式说明**
#format_instructions 是一段自动生成的提示，告诉模型必须输出 JSON，并给出 schema
from langchain_core.output_parsersi import PydanticOutputParser
parser = PydanticOutputParser(pydantic_object=Diagnosis)
format_instructions = parser.get_format_instructions()
#3.把格式说明写入Prompt
from langchain_core.prompts import PromptTemplate
template = PromptTemplate.from_template(
    #三引号多行字符串
    """请根据以下故障现象给出诊断结果。
故障现象：{symptom}
{format_instructions}
"""
)
prompt_value = template.invoke({
    "symptom":"服务器CPU过高，响应慢",
    "format_instructions":format_instructions,
})
#4.调用大模型获取结果并解析
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    base_url="https://api.dashscope.com",
    api_key="sk-xxxxxxxxxxxxxxxxxxxxxxxx",
    temperature=0.7
)#Model 获取模型
response = llm.invoke(prompt_value)#Prompt prompt_value是PromptValue对象，包含了最终的prompt文本和变量值
diagnosis = parser.invoke(response)#Parser 解析器解析response，返回一个Diagnosis对象
print(diagnosis.root_cause)
print(diagnosis.recommendations)
#解析失败怎么办
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnable import RunnableLambda
parser = PydanticOutputParser(pydantic_object=Diagnosis)
    #runnable:如果解析失败，调用runnable来处理,fallback到字符串
safe_parser = parser.with_fallback([RunnableLambda(lambda x:{"raw":x.content})])


