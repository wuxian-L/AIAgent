#Runnable组件

#Runnable 的通用接口
chain.invoke(input)        # 同步单条
chain.ainvoke(input)       # 异步单条
chain.stream(input)        # 同步流式
chain.astream(input)       # 异步流式
chain.batch(inputs)        # 同步批量
chain.abatch(inputs)       # 异步批量

#Runnable 的 .with_config
#可以给 Runnable 附加运行时配置，例如标签、元数据：
chain_with_meta = chain.with_config({"run_name": "intro_chain"})

#1.RunnableLambda:将一个函数包装为Runnable
#链中插入自定义Python函数
from langchain_core.runnable import RunnableLambda
def add_greeting(input:dict)->dict:
    input["greeting"] = "你好,"
    return input
greeting_step = RunnableLambda(add_greeting)
chain = greeting_step | prompt | llm | parser
#2.RunnablePassthrough:透传输入
#想把输入原样传给下一步，同时附加一些字段
#多Agent协作？
from langchain_core.runnables import RunnablePassthrough
chain = RunnablePassthrough.assign(count = lambda x:len(x["topic"])) | prompt | llm | parser
result = chain.invoke({"role":"专家","topic":"LangChain"})
#x就是{"role":"专家","topic":"LangChain"}
#3.RunnableParallel:并行执行多个分支
#一个输入多种处理 
from langchain_core.runnable import RunnableParallel
parallel = RunnableParallel(
    summary = summary_chain,
    keywords = keywords_chain,
)
result = parallel.ivoke({"topic":"LangChain"})
print(result["summary"])
print(result["keywords"])
#4.RunnableBranch:条件分支
#RunnableBranch 会按顺序判断条件，第一个为 True 的分支会被执行
from langchain_core.runnables import RunnableBranch
branch = RunnableBranch(
    (lambda x: x["language"] == "中文",chinese_chain),
    (lambda x: x["language"] == "英文",english_chain),
    default_chain,
)
result = branch.invoke({"language":"中文","topic":"LangChain"})
#5.RunnableSequence(隐式创建，不必在意)
#当你写 a | b | c 时，LangChain 内部会创建一个 RunnableSequence。也可以显式创建：
from langchain_core.runnables import RunnableSequence
chain = RunnableSequence(
    first = prompt,
    middle = [llm],
    last = parser,
)
'''
不同类型的 Runnable 接受不同类型的输入：

Runnable	            典型输入	                        典型输出
PromptTemplate	        dict	                        StringPromptValue
ChatPromptTemplate	    dict	                        ChatPromptValue
ChatOpenAI	            str 或 list[BaseMessage] 或 ChatPromptValue	    AIMessage
StrOutputParser	        AIMessage / str	                str
PydanticOutputParser	AIMessage / str	                Pydantic 对象
'''


