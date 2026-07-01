#常见读取配置方式
#加载 并 读取
import dotenv
dotenv.load_dotenv()
os.getenv()
#BaseSetting方式
'''
BaseSettings 会自动做什么
读取 .env 文件：根据 env_file 路径加载
读取环境变量：如果系统环境变量中存在，优先级更高
自动类型转换：把字符串 "True" 转成 True，"9900" 转成 9900
使用默认值：如果 .env 和环境变量都没有，使用字段默认值
数据校验：如果值类型不对，会抛出 ValidationError
'''
class Settings(BaseSettings)

from pydantic_settings import BaseSettings,SettingsConfigDict
class Setting(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        #case_sensitive=False 时，DASHSCOPE_API_KEY 会自动映射到 dashscope_api_key
        case_sensitive = False,#环境变量习惯大写 但Python字段习惯小写
        #如果 .env 里有一些配置在 Settings 类里没有定义，默认会报错
        #但如果extra="ignore" 表示忽略这些未定义字段，不会报错。
        extra = "ignore",
    )
    app_name:str = "MyApp"
    debug:bool = False
    port:int = 8000
config = Settings()

#项目配置解读
from typing import Dict,Any
from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    '''应用配置'''
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        case_sensitive = False,
        extra = "ignore",
    )
    #应用配置
    app_name:str = "SuperBizAgent"
    app_version:str = "1.0.0"
    debug:bool = False
    host:str = "0.0.0.0"
    port:int = 9900
    
    #DashScope配置 阿里云百炼平台
    dashscope_api_key:str = ""
    dashscope_model:str = "qwen-max"
    dashscope_embedding_model:str = "text-embedding-v4"

    #Milvus配置
    milvus_host:str = "localhost"
    milvus_port:int = 19530
    milvus_timeout:int = 10000#毫秒

    #RAG
    rag_top_k: int = 3
    rag_model: str = "qwen-max"

    #文档分块配置
    chunk_max_size:int = 800
    chunk_overlap:int = 100

    # MCP 服务配置（transport: stdio | sse | streamable-http）
    # 腾讯云托管 MCP 的 URL 通常含 /sse/，需使用 sse；本地 FastMCP 使用 streamable-http
    # MCP模型上下文协议，标准化模型调用
    mcp_cls_transport:str = "streamable-http"
    mcp_cls_url:str = "http://localhost:8003/mcp"
    mcp_monitor_transport:str = "streamable-http"
    mcp_monitor_url:str = "http://localhost:8004/mcp"

    #Promptheus
    prometheus_base_url:str = "http://127.0.0.1:9090"
    prometheus_request_timeout: float = 10.0

    @property
    def mcp_servers(self)->Dict[str,Dict[str,Any]]:
        '''获取完整的MCP服务器配置'''
        return{
            "cls":{
                "transport":self.mcp_cls_transport,
                "url":self.mcp_cls_url,
            },
            "monitor":{
                "transport":self.mcp_cls_transport,
                "url":self.mcp_cls_url,
            },
        }

config = Settings()










