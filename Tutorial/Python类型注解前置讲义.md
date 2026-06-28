# AIAgent 前置知识补充讲义 · Python 类型注解

> 本讲义为 AIAgent 项目实战课程的前置知识补充
> 目标：系统掌握 Python 类型注解，理解其在 FastAPI / Pydantic 中的应用
> 适用对象：有 Java 背景、需要查漏补缺的同学
> 建议学习时长：90-120 分钟（理论 + 实验）

---

## 1. 什么是类型注解

类型注解（Type Hints）是 Python 3.5+ 引入的特性，用于在代码中标注变量、函数参数和返回值的类型。

类型注解的特点是：

- **不会强制类型检查**：Python 仍然是动态类型语言，注解不会被运行时强制执行
- **辅助开发**：让代码更易读、更易维护
- **工具支持**：IDE、静态类型检查器（mypy）、FastAPI/Pydantic 可以利用注解做很多事

### 1.1 一个简单的例子

没有类型注解：

```python
def add(a, b):
    return a + b
```

有类型注解：

```python
def add(a: int, b: int) -> int:
    return a + b
```

这里：

- `a: int` 表示参数 `a` 应该是整数
- `b: int` 表示参数 `b` 应该是整数
- `-> int` 表示函数返回值是整数

### 1.2 类型注解 vs Java 类型声明

| 语言 | 语法 | 是否运行时强制 |
|------|------|--------------|
| Java | `int add(int a, int b)` | 是 |
| Python | `def add(a: int, b: int) -> int:` | 否 |

Python 的类型注解更像"建议"或"文档"，而 Java 的类型声明是编译器强制的。

---

## 2. 为什么需要类型注解

### 2.1 提高代码可读性

```python
def process(data):
    ...
```

看完这个函数签名，你不知道 `data` 是什么类型。

```python
def process(data: list[dict[str, str]]) -> bool:
    ...
```

加了类型注解后，一眼就知道：`data` 是一个列表，列表元素是字典，字典的键值都是字符串，函数返回布尔值。

### 2.2 IDE 智能提示

类型注解让 IDE 能提供更准确的代码补全和错误提示。

### 2.3 静态类型检查

可以用 mypy 等工具在运行前检查类型错误：

```bash
pip install mypy
mypy my_script.py
```

### 2.4 FastAPI / Pydantic 依赖类型注解

这是对我们来说最重要的原因。FastAPI 和 Pydantic 大量依赖类型注解：

- 自动校验请求参数类型
- 自动生成 API 文档
- 自动序列化响应数据

---

## 3. 基础类型注解

### 3.1 变量类型注解

```python
name: str = "张三"
age: int = 25
height: float = 1.75
is_student: bool = True
```

### 3.2 函数参数和返回值注解

```python
def greet(name: str) -> str:
    return f"Hello, {name}"

print(greet("张三"))  # Hello, 张三
```

### 3.3 无返回值

```python
def log(message: str) -> None:
    print(message)
```

### 3.4 任意类型

```python
from typing import Any

def process(value: Any) -> Any:
    return value
```

`Any` 表示任意类型，相当于 Java 中的 `Object`。

---

## 4. 容器类型注解

### 4.1 List（列表）

```python
from typing import List

# Python 3.9+ 可以直接用内置类型
numbers: list[int] = [1, 2, 3]
names: list[str] = ["张三", "李四"]

# Python 3.8 及更早版本需要用 typing.List
numbers_old: List[int] = [1, 2, 3]
```

### 4.2 Dict（字典）

```python
from typing import Dict

# Python 3.9+
user_ages: dict[str, int] = {"张三": 25, "李四": 30}

# Python 3.8 及更早
user_ages_old: Dict[str, int] = {"张三": 25, "李四": 30}
```

### 4.3 Tuple（元组）

```python
from typing import Tuple

# 固定长度的元组
point: tuple[int, int] = (10, 20)

# 可变长度的元组
numbers: tuple[int, ...] = (1, 2, 3, 4)
```

### 4.4 Set（集合）

```python
tags: set[str] = {"python", "fastapi", "ai"}
```

### 4.5 Optional（可选类型）

```python
from typing import Optional

# 表示 age 可以是 int 或 None
age: Optional[int] = None

# Python 3.10+ 推荐写法
age_new: int | None = None
```

`Optional[int]` 等价于 `int | None`（Python 3.10+），表示"整数或空值"。

### 4.6 Union（联合类型）

```python
from typing import Union

# 表示 value 可以是 int 或 str
value: Union[int, str] = 123

# Python 3.10+ 推荐写法
value_new: int | str = 123
```

---

## 5. 高级类型注解

### 5.1 Callable（可调用对象）

```python
from typing import Callable

# 表示一个接受两个 int 参数、返回 int 的函数
adder: Callable[[int, int], int] = lambda x, y: x + y

def execute(a: int, b: int, func: Callable[[int, int], int]) -> int:
    return func(a, b)
```

### 5.2 TypeVar（类型变量）

```python
from typing import TypeVar, List

T = TypeVar("T")

def first(items: List[T]) -> T:
    return items[0]

print(first([1, 2, 3]))      # int
print(first(["a", "b"]))     # str
```

这类似于 Java 的泛型方法。

### 5.3 Generic（泛型类）

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Box(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value
    
    def get(self) -> T:
        return self.value

int_box: Box[int] = Box(123)
str_box: Box[str] = Box("hello")
```

### 5.4 自定义类型别名

```python
from typing import Dict, List

# 定义类型别名
UserInfo = Dict[str, str]
UserList = List[UserInfo]

users: UserList = [
    {"name": "张三", "email": "zhangsan@example.com"},
    {"name": "李四", "email": "lisi@example.com"}
]
```

Python 3.10+ 推荐用 `type` 关键字：

```python
type UserInfo = dict[str, str]
type UserList = list[UserInfo]
```

---

## 6. 类中的类型注解

### 6.1 类属性注解

```python
class User:
    name: str
    age: int
    
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age
    
    def is_adult(self) -> bool:
        return self.age >= 18
```

### 6.2 方法返回 self

```python
from typing import Self

class User:
    def __init__(self, name: str) -> None:
        self.name = name
    
    def set_name(self, name: str) -> Self:
        self.name = name
        return self
```

`Self` 是 Python 3.11+ 引入的，表示返回当前类的实例。

---

## 7. 与 Java 类型系统的对比

| 概念 | Python | Java |
|------|--------|------|
| 整数 | `int` | `int` / `Integer` |
| 字符串 | `str` | `String` |
| 列表 | `list[T]` | `List<T>` |
| 字典 | `dict[K, V]` | `Map<K, V>` |
| 可选 | `T \| None` | `Optional<T>` |
| 任意类型 | `Any` | `Object` |
| 泛型类 | `class Box(Generic[T])` | `class Box<T> {}` |
| 类型检查 | 静态（mypy）+ 运行时（Pydantic） | 编译时 |

Python 类型注解的语法越来越像 Java，但记住它是"建议"而非强制。

---

## 8. Pydantic 中的类型注解

### 8.1 Pydantic 基础模型

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    email: str | None = None

# 自动类型校验和转换
user = User(name="张三", age="25")  # "25" 会被自动转成 25
print(user.age)  # 25

# 类型错误会抛出异常
try:
    user = User(name="张三", age="not_a_number")
except ValueError as e:
    print(e)
```

### 8.2 Field 配置

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    id: int = Field(..., description="用户 ID")
    name: str = Field(..., min_length=2, max_length=50)
    age: int = Field(..., ge=0, le=150)
    email: str | None = Field(default=None, description="邮箱")
```

`Field` 参数：

- `...` 表示必填
- `default=...` 设置默认值
- `description` 字段描述
- `min_length` / `max_length` 字符串长度限制
- `ge` / `le` 数值范围限制（greater/less equal）

### 8.3 嵌套模型

```python
from pydantic import BaseModel

class Address(BaseModel):
    city: str
    zipcode: str

class User(BaseModel):
    name: str
    age: int
    address: Address

user = User(
    name="张三",
    age=25,
    address={"city": "北京", "zipcode": "100000"}
)
print(user.address.city)  # 北京
```

### 8.4 项目中的应用

看 `app/models/request.py`：

```python
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    id: str = Field(..., description="会话 ID", alias="Id")
    question: str = Field(..., description="用户问题", alias="Question")

    class Config:
        populate_by_name = True
```

这里：

- `id` 和 `question` 都是必填字符串
- `alias="Id"` 表示接口接收的 JSON 字段名是大写的 `Id`
- `populate_by_name = True` 表示既可以用别名也可以用属性名

---

## 9. FastAPI 中的类型注解

### 9.1 路径参数

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}
```

FastAPI 会自动把 URL 中的 `user_id` 转成整数。如果传入 `abc`，会返回 422 错误。

### 9.2 查询参数

```python
@app.get("/users")
async def list_users(page: int = 1, size: int = 10):
    return {"page": page, "size": size}
```

### 9.3 请求体

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

@app.post("/users")
async def create_user(user: User):
    return user
```

### 9.4 响应模型

```python
from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    name: str

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    return {"id": user_id, "name": "张三", "password": "secret"}
```

即使返回字典包含 `password`，响应中也不会包含，因为 `UserResponse` 没有这个字段。

---

## 10. 常见类型注解写法速查

```python
from typing import Any, Callable, Optional, Union, List, Dict, Tuple

# 基础类型
x: int = 1
y: str = "hello"
z: float = 3.14
flag: bool = True
nothing: None = None
anything: Any = "可以是任何类型"

# 容器类型
nums: list[int] = [1, 2, 3]
user: dict[str, str] = {"name": "张三"}
point: tuple[int, int] = (0, 0)
tags: set[str] = {"a", "b"}

# 可选类型
maybe_age: int | None = None
maybe_name: Optional[str] = None

# 联合类型
value: int | str = 123
result: Union[int, str] = "ok"

# 函数类型
def add(a: int, b: int) -> int:
    return a + b

handler: Callable[[int, int], int] = add

# 异步函数
async def fetch(url: str) -> dict[str, Any]:
    return {"url": url}
```

---

## 11. 动手实验

### 实验 1：基础类型注解

```python
def calculate_area(width: float, height: float) -> float:
    return width * height

area: float = calculate_area(3.5, 4.0)
print(area)
```

### 实验 2：容器类型

```python
from typing import List, Dict

def count_words(words: List[str]) -> Dict[str, int]:
    result: Dict[str, int] = {}
    for word in words:
        result[word] = result.get(word, 0) + 1
    return result

words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
print(count_words(words))
```

### 实验 3：Pydantic 模型

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    quantity: int = Field(default=0, ge=0)

product = Product(name="笔记本电脑", price="5999.00", quantity=10)
print(product.model_dump())

# 测试错误数据
try:
    Product(name="", price=-100)
except ValueError as e:
    print("校验失败:", e)
```

### 实验 4：FastAPI 类型校验

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(req: LoginRequest):
    return {"message": f"欢迎，{req.username}"}
```

启动后访问 `/docs`，用 Swagger UI 测试：

- 正确请求：`{"username":"admin","password":"123456"}`
- 错误请求：`{"username":"admin"}`（缺少 password，会报 422）

### 实验 5：用 mypy 做静态检查

```python
# test_type.py
def add(a: int, b: int) -> int:
    return a + b

result = add("1", "2")  # 类型不匹配，但 Python 运行不会报错
```

运行 mypy：

```bash
pip install mypy
mypy test_type.py
```

mypy 会提示类型错误。

---

## 12. 学习检查清单

完成本讲义后，请确认你能回答以下问题：

- [ ] Python 类型注解和 Java 类型声明有什么区别？
- [ ] 如何给函数参数和返回值添加类型注解？
- [ ] `Optional[int]` 和 `int | None` 有什么区别？
- [ ] `list[int]` 和 `List[int]` 分别适用于什么 Python 版本？
- [ ] `Any` 是什么？相当于 Java 中的什么？
- [ ] Pydantic 如何利用类型注解做数据校验？
- [ ] FastAPI 如何利用类型注解做参数校验和文档生成？
- [ ] `Field(...)` 中的 `...` 表示什么？

---

## 13. 下节课衔接

学完类型注解后，你已经具备了学习 FastAPI 的全部前置知识：

- HTTP 协议 → 理解请求响应
- JSON → 理解数据交换格式
- 类型注解 → 理解 FastAPI / Pydantic 的自动校验
- 异步编程 → 理解 FastAPI 的 `async def`
- RESTful API → 理解接口设计

建议继续学习 **AIAgent 第 4 课：FastAPI 架构与应用入口**。

---

*生成时间：2026/06/28*
*用途：AIAgent 项目实战课程前置知识补充*
