from fastapi import FastAPI
from fastapi.middleware.cores import CORSMiddleware
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from app.config import config 
from longuru import logger
from app.api import chat,health,file,aiops
from app.core.milvus_client import milvus_manager

@asynccontextmanager
async def lifespan(app:FastAPI):
    # 启动时执行
    logger.info("=" * 60)
    logger.info(f"🚀 {config.app_name} v{config.app_version} 启动中...")
    logger.info(f"📝 环境: {'开发' if config.debug else '生产'}")
    logger.info(f"🌐 监听地址: http://{config.host}:{config.port}")
    logger.info(f="📚 API 文档: http://{config.host}:{config.port}/docs")

    #链接Milvus数据库
    logger.info("正在连接Milvus数据库")
    milvus_manager.connect()
    logger.info("Milvus连接成功")

    logger.info("="*60)

    yield

    #关闭时执行
    logger.info("🔌 正在关闭 Milvus 连接...")
    milvus_manager.close()
    logger.info(f"👋 {config.app_name} 关闭")

#创建FastAPI应用
app = FastAPI(
    title = config.app_name,
    version = config.app_version,
    description="基于LangChain的智能oncall运维系统",
    lifespan = lifespan#函数对象参数
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#注册路由
#最终路径 =注册时的 prefix + 路由定义时的 prefix + 路由路径
#例： /api(注册时)/chat(定义时)/路由(调用时)
app.include_router(health.router,tag=["健康检查"])
app.include_router(chat.router,prefix="/api",tags=["对话"])
app.include_router(chat.router,prefix="/api",tags=["文件管理"])
app.include_router(chat.router,prefix="/api",tags=["AIOps智能运维"])

#挂载静态文件
static_dir = "static"
app.mount("/static",#URL路径，浏览器访问使用
          StaticFiles(directory=static_dir),#静态文件处理器，static_dir,本地服务器文件位置
          name="static"#app(FastAPI)内部名称，无用
)

@app.get("/")
async def root():
    '''返回首页'''
    index_path = os.path.join(static_dir,"index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return{
        "message":f"Welcome to {config.app_name}API"
        "version":config.app_version,
        "docs":"/docs"
    }
if __name__ = "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=config.host,
        port=config.port,
        reload=config.debug,
        log_level="info"
    )

'''
配置资源： 定义上下文管理器、创建FastAPI
定义中间件：配置CORS
连接后端：注册路由
加载前端：挂载静态文件


'''