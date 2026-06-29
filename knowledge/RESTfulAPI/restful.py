#FastAPI中的RESTful实践
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
app = FastAPI()
'''
BaseModel是 Pydantic 提供的「数据模型基类」，用来定义 数据结构 + 数据校验规则
FastAPI 会自动：
✅ 类型检查 name必须是字符串
✅ 必填校验 不传 email会报错
✅ JSON ↔ Python 对象转换请求 JSON → User对象
✅ 自动生成 OpenAPI 文档    Swagger UI
✅ IDE 智能提示 user.name、user.email
'''
#定义一个「用户数据模型」
class User(BaseModel):
    id:int|None = None#id 可以是 int 或 None ，默认为None
    name:str
    email:str

users = {}
next_id = 1

@app.get("/users")
def list_users():
    return list(users.values())
@app.get("/users/{user_id}")
def get_user(user_id:int):
    if user_id not in users:
        raise HTTPException(status_code=404,detail="用户不存在")
    return users[user_id]

@app.post("/users",status_code=201)
def create_user(user:User):
    global next_id
    new_user = user.model_copy(updata={"id":next_id})
    users[next_id] = new_user
    next_id+=1
    return new_user
@app.put("/user/{user_id}")
def updata_user(user_id:int,user:User):
    if user_id not in users:
        raise HTTPException(status_code=404,detail = "用户不存在")
    users[user_id] = user.model_copy(update = {"id":user_id})
    return users[user_id]
@app.delete("/user/{user_id}",status_code=204)
def delete_user(user_id:int):
    if user_id not in users:
        raise HTTPException(status_code=404,detail="用户不存在")
    del users[user_id]
    return None


#路径参数（URL中）和查询参数
from fastapi import FastAPI
app = FastAPI()
#路径参数
@app.get("/users/{user_id}")
async def get_user(user_id:int)
    return {"user_id":user_id}
#查询参数
@app.get("/users")
async def list_users(page:int = 1,size:int = 10):
    return {"page":page,"size":size}
'''
/users/123 → user_id=123
/users?page=2&size=20 → page=2, size=20
'''

#请求体 req
from pydantic import BaseModel
class CreateUserRequest(BaseModel):
    name:str
    email:str
@app.post("/users")
async def create_user(req: CreateUserRequest):
    return {"name":req.name,"email":req.email}



