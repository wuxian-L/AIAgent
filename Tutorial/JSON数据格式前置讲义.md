# AIAgent 前置知识补充讲义 · JSON 数据格式

> 本讲义为 AIAgent 项目实战课程的前置知识补充
> 目标：系统掌握 JSON 数据格式，理解 Python/Java 中的 JSON 处理，以及 FastAPI/Pydantic 中的自动序列化
> 适用对象：有 Java 背景、需要查漏补缺的同学
> 建议学习时长：60-90 分钟（理论 + 实验）

---

## 1. JSON 是什么

JSON（JavaScript Object Notation，JavaScript 对象表示法）是一种**轻量级的数据交换格式**。

它基于 JavaScript 的对象语法，但独立于语言，几乎所有编程语言都支持 JSON。

JSON 的主要特点：

- **易读**：纯文本格式，人类可读
- **轻量**：相比 XML 更简洁
- **通用**：跨语言、跨平台
- **自描述**：数据结构清晰

---

## 2. 为什么 API 都喜欢用 JSON

在 Web 开发中，JSON 是最常用的数据交换格式：

1. **前后端分离**：前端用 JavaScript，天然支持 JSON
2. **移动应用**：App 与服务器通信常用 JSON
3. **微服务**：服务之间调用常用 JSON
4. **配置文件**：很多工具用 JSON 作为配置格式

在我们的 AIAgent 项目中：

- 调用大模型 API 的请求和响应都是 JSON
- FastAPI 接口的请求体和响应体都是 JSON
- Milvus 等数据库的交互也常使用 JSON 格式

---

## 3. JSON 数据类型

JSON 只支持以下几种数据类型：

| 类型 | 示例 | 说明 |
|------|------|------|
| 字符串（string） | `"hello"` | 必须用双引号包裹 |
| 数字（number） | `123`, `3.14` | 整数或浮点数 |
| 布尔（boolean） | `true`, `false` | 全小写 |
| 空值（null） | `null` | 表示空 |
| 对象（object） | `{"name":"张三"}` | 键值对集合 |
| 数组（array） | `[1, 2, 3]` | 有序列表 |

### 3.1 字符串

```json
"Hello, World"
"张三"
"This is a \"quoted\" word"
```

注意：

- JSON 字符串必须用**双引号**
- 特殊字符需要转义，如 `"` 写成 `\"`，换行写成 `\n`

### 3.2 数字

```json
42
3.14159
-10
1.5e10
```

### 3.3 布尔和空值

```json
true
false
null
```

**注意**：JSON 中是 `true` / `false` / `null`，Python 中是 `True` / `False` / `None`，Java 中是 `true` / `false` / `null`。

### 3.4 对象

对象是键值对的集合，用大括号 `{}` 包裹。

```json
{
    "name": "张三",
    "age": 25,
    "isStudent": false,
    "address": null
}
```

规则：

- 键必须是字符串，用双引号包裹
- 键值对之间用逗号分隔
- 最后一个键值对后面不能加逗号（严格 JSON 语法）

### 3.5 数组

数组是有序的值的集合，用中括号 `[]` 包裹。

```json
[1, 2, 3, 4, 5]

[
    {"name": "张三", "age": 25},
    {"name": "李四", "age": 30}
]
```

数组中可以放任意 JSON 类型，包括对象和嵌套数组。

---

## 4. JSON 语法规则

写 JSON 时需要注意以下规则：

1. **数据由键值对组成**：`"key": value`
2. **键必须是双引号字符串**
3. **值可以是任意 JSON 类型**
4. **键值对之间用逗号分隔**
5. **对象用 `{}` 包裹**
6. **数组用 `[]` 包裹**
7. **JSON 中不能写注释**
8. ** trailing comma（末尾逗号）不允许**

### 4.1 正确的 JSON

```json
{
    "name": "张三",
    "age": 25,
    "hobbies": ["读书", "游泳", "编程"],
    "address": {
        "city": "北京",
        "zipcode": "100000"
    },
    "isMarried": false
}
```

### 4.2 错误的 JSON

```json
{
    name: "张三",        // 错误：键没有用双引号
    'age': 25,           // 错误：键用了单引号
    "hobbies": ["读书",] // 错误：末尾多余逗号
    "isMarried": False   // 错误：JSON 中是 false，不是 False
}
```

---

## 5. JSON 与 Python 的映射

Python 内置了 `json` 模块来处理 JSON 数据。

### 5.1 类型映射表

| JSON | Python |
|------|--------|
| string | `str` |
| number | `int` / `float` |
| boolean | `bool` |
| null | `None` |
| object | `dict` |
| array | `list` |

### 5.2 JSON 字符串 → Python 对象（反序列化）

```python
import json

json_str = '{"name": "张三", "age": 25, "is_student": false}'
data = json.loads(json_str)

print(data)          # {'name': '张三', 'age': 25, 'is_student': False}
print(type(data))    # <class 'dict'>
print(data["name"])  # 张三
```

`json.loads()` 把 JSON 字符串解析成 Python 对象。

### 5.3 Python 对象 → JSON 字符串（序列化）

```python
import json

data = {
    "name": "张三",
    "age": 25,
    "hobbies": ["读书", "游泳"],
    "is_student": False
}

json_str = json.dumps(data)
print(json_str)
# {"name": "张三", "age": 25, "hobbies": ["读书", "游泳"], "is_student": false}
```

`json.dumps()` 把 Python 对象转换成 JSON 字符串。

### 5.4 美化输出

```python
import json

data = {"name": "张三", "age": 25, "hobbies": ["读书", "游泳"]}

# 缩进美化
pretty = json.dumps(data, ensure_ascii=False, indent=2)
print(pretty)
```

输出：

```json
{
  "name": "张三",
  "age": 25,
  "hobbies": [
    "读书",
    "游泳"
  ]
}
```

参数说明：

- `ensure_ascii=False`：允许输出中文，不转义成 Unicode
- `indent=2`：用 2 个空格缩进

### 5.5 读写 JSON 文件

```python
import json

# 写入 JSON 文件
data = {"name": "张三", "age": 25}
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 读取 JSON 文件
with open("data.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)
print(loaded)
```

注意：

- `json.dumps()` / `json.loads()` 处理字符串
- `json.dump()` / `json.load()` 处理文件对象

---

## 6. JSON 与 Java 的映射

| JSON | Java |
|------|------|
| string | `String` |
| number | `int` / `long` / `double` / `BigDecimal` |
| boolean | `boolean` / `Boolean` |
| null | `null` |
| object | `Map` / 自定义对象 |
| array | `List` / 数组 |

Java 中常用 Jackson 或 Gson 处理 JSON：

```java
// Jackson 示例
ObjectMapper mapper = new ObjectMapper();
String json = "{\"name\":\"张三\",\"age\":25}";
User user = mapper.readValue(json, User.class);
String output = mapper.writeValueAsString(user);
```

Python 的 `json` 模块相当于 Java 中 Jackson 的基础功能，但更加轻量。

---

## 7. JSON 与 XML、YAML 对比

| 特性 | JSON | XML | YAML |
|------|------|-----|------|
| 可读性 | 好 | 一般 | 很好 |
| 简洁性 | 好 | 较差 | 很好 |
| 支持注释 | 否 | 是 | 是 |
| 数据类型 | 简单 | 都是字符串 | 较丰富 |
| 解析难度 | 简单 | 较复杂 | 较复杂 |
| 适用场景 | API 数据交换 | 配置、文档 | 配置文件 |

在 Web API 中，JSON 是主流选择。

---

## 8. FastAPI / Pydantic 中的 JSON

### 8.1 自动 JSON 序列化

FastAPI 会自动把 Pydantic 模型或 Python 字典转换成 JSON 响应：

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    name: str
    age: int

@app.get("/user")
async def get_user():
    return User(name="张三", age=25)
```

访问这个接口，响应自动是：

```json
{
  "name": "张三",
  "age": 25
}
```

FastAPI 会自动设置响应头：

```http
Content-Type: application/json
```

### 8.2 自动 JSON 反序列化

FastAPI 会自动把请求体中的 JSON 转换成 Pydantic 模型：

```python
from pydantic import BaseModel

class CreateUserRequest(BaseModel):
    name: str
    age: int

@app.post("/users")
async def create_user(req: CreateUserRequest):
    return {"message": f"创建用户 {req.name} 成功"}
```

如果客户端发送：

```json
{"name": "张三", "age": 25}
```

FastAPI 会自动解析成 `CreateUserRequest` 对象。

如果发送：

```json
{"name": "张三", "age": "不是数字"}
```

FastAPI 会自动返回 422 错误：

```json
{
  "detail": [
    {
      "loc": ["body", "age"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
```

### 8.3 Pydantic 模型转 JSON

```python
from pydantic import BaseModel
import json

class User(BaseModel):
    name: str
    age: int

user = User(name="张三", age=25)

# 方法 1：model_dump 转字典
print(user.model_dump())  # {'name': '张三', 'age': 25}

# 方法 2：model_dump_json 转 JSON 字符串
print(user.model_dump_json())  # {"name":"张三","age":25}
print(user.model_dump_json(ensure_ascii=False))  # {"name":"张三","age":25}
```

Pydantic v2 中：

- `model_dump()` 替代了旧的 `dict()`
- `model_dump_json()` 替代了旧的 `json()`

---

## 9. 常见错误与注意事项

### 9.1 单引号问题

JSON 标准中字符串和键必须用双引号。

```python
import json

# 错误
json_str = "{'name': '张三'}"
data = json.loads(json_str)  # JSONDecodeError

# 正确
json_str = '{"name": "张三"}'
data = json.loads(json_str)
```

### 9.2 末尾逗号问题

严格 JSON 不允许末尾逗号。

```python
import json

json_str = '["a", "b", ]'  # 错误
data = json.loads(json_str)  # JSONDecodeError
```

### 9.3 Python 元组转 JSON

JSON 中没有元组类型，Python 元组会被转成数组。

```python
import json

data = {"items": (1, 2, 3)}
print(json.dumps(data))  # {"items": [1, 2, 3]}
```

### 9.4 自定义对象不能直接序列化

```python
import json
from datetime import datetime

now = datetime.now()
json.dumps({"time": now})  # TypeError: Object of type datetime is not JSON serializable
```

解决：自定义序列化函数。

```python
import json
from datetime import datetime

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

now = datetime.now()
print(json.dumps({"time": now}, cls=MyEncoder))
```

### 9.5 JSON 中没有日期类型

JSON 本身没有日期类型，通常用字符串表示：

```json
{
    "created_at": "2026-06-28T10:30:00"
}
```

Pydantic 可以自动把 ISO 格式字符串解析成 `datetime` 对象。

---

## 10. 在 httpx 中使用 JSON

httpx 可以方便地发送和接收 JSON：

```python
import httpx

# 发送 JSON
response = httpx.post(
    "https://httpbin.org/post",
    json={"name": "张三", "age": 25}
)

# 接收 JSON
print(response.json())
```

注意：

- `json=` 参数会自动设置 `Content-Type: application/json`
- 自动把 Python 字典序列化成 JSON 字符串
- `response.json()` 自动把响应体解析成 Python 对象

---

## 11. 项目中的应用

### 11.1 项目请求模型

看 `app/models/request.py`：

```python
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    id: str = Field(..., description="会话 ID", alias="Id")
    question: str = Field(..., description="用户问题", alias="Question")
```

这个 Pydantic 模型对应客户端发送的 JSON：

```json
{
    "Id": "session-123",
    "Question": "什么是向量数据库？"
}
```

### 11.2 项目响应示例

调用 `/api/chat` 后，服务器可能返回：

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "answer": "向量数据库是一种专门用于存储和检索向量数据的数据库..."
    }
}
```

---

## 12. 动手实验

### 实验 1：JSON 解析与生成

```python
import json

# 定义一个 Python 字典
user = {
    "name": "张三",
    "age": 25,
    "is_student": False,
    "scores": [85, 90, 78],
    "address": {
        "city": "北京",
        "zipcode": "100000"
    }
}

# 序列化为 JSON 字符串
json_str = json.dumps(user, ensure_ascii=False, indent=2)
print(json_str)

# 反序列化为 Python 对象
parsed = json.loads(json_str)
print(parsed["address"]["city"])
```

### 实验 2：用 Pydantic 处理 JSON

```python
from pydantic import BaseModel
import json

class Address(BaseModel):
    city: str
    zipcode: str

class User(BaseModel):
    name: str
    age: int
    is_student: bool
    address: Address

json_str = '{"name":"张三","age":25,"is_student":false,"address":{"city":"北京","zipcode":"100000"}}'
user = User.model_validate_json(json_str)
print(user.model_dump())
```

### 实验 3：httpx 发送和接收 JSON

```python
import httpx

response = httpx.post(
    "https://httpbin.org/post",
    json={"name": "张三", "age": 25}
)

data = response.json()
print(data["json"])  # 服务器回显的 JSON 数据
```

### 实验 4：读写 JSON 文件

```python
import json

users = [
    {"name": "张三", "age": 25},
    {"name": "李四", "age": 30}
]

with open("users.json", "w", encoding="utf-8") as f:
    json.dump(users, f, ensure_ascii=False, indent=2)

with open("users.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)
    print(loaded)
```

---

## 13. 学习检查清单

完成本讲义后，请确认你能回答以下问题：

- [ ] JSON 有哪些基本数据类型？
- [ ] JSON 字符串为什么必须用双引号？
- [ ] Python 中如何把字典转成 JSON 字符串？
- [ ] Python 中如何把 JSON 字符串转成字典？
- [ ] `ensure_ascii=False` 的作用是什么？
- [ ] FastAPI 如何自动处理请求体中的 JSON？
- [ ] Pydantic 模型如何转成 JSON 字符串？
- [ ] JSON 中没有哪些类型？日期通常怎么表示？

---

## 14. 下节课衔接

学完 JSON 后，建议继续学习 **Python 类型注解**，因为 FastAPI 和 Pydantic 大量依赖类型注解来实现自动校验和文档生成。

---

*生成时间：2026/06/28*
*用途：AIAgent 项目实战课程前置知识补充*
