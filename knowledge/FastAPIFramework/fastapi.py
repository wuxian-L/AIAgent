from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel,Field
'''
#Field用法
...             必填
default=None    可选
gt / ge / lt / le   数值范围
min_length / max_length 字符串长度
pattern     正则校验
description 文档说明
aliasJSON   字段别名
examples    示例值
'''
from pydantic import Field
class User(BaseModel):
    id: int = Field(..., gt=0, description="用户ID")
    name: str = Field(..., min_length=1, max_length=20)
    age: int | None = Field(None, ge=0, le=150)
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
#定义生命周期管理
@asynccontextmanager
async def lifespan(app:FastAPI):
    print("应用启动中")
    await innit_database()
    yield
    print("应用关闭中")
    await close_database()
app = FastAPI(lifespan = lifespan)
    