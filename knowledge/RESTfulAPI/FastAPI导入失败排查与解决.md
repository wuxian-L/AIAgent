# FastAPI 导入失败排查与解决

> 对应文件：`knowledge\RESTfulAPI\lab.py`  
> 报错信息：`ModuleNotFoundError: No module named 'fastapi'`

---

## 1. 问题现象

运行 `lab.py` 或直接 `import fastapi` 时抛出：

```
ModuleNotFoundError: No module named 'fastapi'
  File "C:\Users\10497\Documents\AIAgent\knowledge\RESTfulAPI\lab.py", line 1, in <module>
    from fastapi import FastAPI
```

奇怪的是，之前明明能运行成功。

---

## 2. 根本原因：Windows 上存在多个 Python 解释器

在 Windows 中，`python`、`python3`、`py` 可能指向**不同的解释器**，每个解释器有自己的 `site-packages`。

本次排查发现系统里至少有两个 Python 3.12：

| 命令 | 实际解释器 | 是否已安装 fastapi/uvicorn |
|------|-----------|---------------------------|
| `python`（当前 Git Bash） | `C:\anaconda\python.exe` | ✅ 已安装 |
| `py`（Windows 启动器默认） | `C:\Users\10497\AppData\Local\Programs\Python\Python312\python.exe` | ❌ 未安装 |

> 之前运行成功，大概率用的是 `python`（Anaconda）；这次报错，是因为实际执行的是 `py` 指向的 Python.org 解释器，而它之前没有安装 `fastapi`。

---

## 3. 排查命令

### 3.1 查看当前 `python` 和 `py` 分别对应哪个解释器

```bash
python -c "import sys; print(sys.executable); print(sys.version)"
py -c "import sys; print(sys.executable); print(sys.version)"
```

### 3.2 查看 fastapi 安装在哪个解释器里

```bash
python -m pip show fastapi
py -m pip show fastapi
```

### 3.3 直接测试 import

```bash
python -c "import fastapi; print(fastapi.__file__)"
py -c "import fastapi; print(fastapi.__file__)"
```

---

## 4. 解决方案

### 方案 A：继续使用已有 fastapi 的解释器（Anaconda）

在 **Git Bash / 当前终端** 中，`python` 已指向 Anaconda，直接执行：

```bash
python -m uvicorn knowledge.RESTfulAPI.lab:app --host 127.0.0.1 --port 8000
```

或在 VS Code 中把解释器切换为：

```
C:\anaconda\python.exe
```

> 注意：当前 Git Bash 里的 `uvicorn` 命令也来自 Anaconda，所以直接 `uvicorn ...` 也能跑。

### 方案 B：在 `py` 默认解释器里也安装 fastapi

如果你想让 `py` 或 `py -m uvicorn` 也能直接运行，需要给这个解释器安装依赖：

```bash
py -m pip install fastapi uvicorn
```

安装完成后验证：

```bash
py -c "import fastapi, uvicorn; print('fastapi', fastapi.__version__); print('uvicorn', uvicorn.__version__)"
```

再按教程方式启动：

```bash
py -m uvicorn knowledge.RESTfulAPI.lab:app --host 127.0.0.1 --port 8000
```

---

## 5. 本次实际操作记录

执行了方案 B：

```bash
py -m pip install fastapi uvicorn
```

安装后验证通过：

```
fastapi 0.138.1 from C:\Users\10497\AppData\Local\Programs\Python\Python312\Lib\site-packages\fastapi\__init__.py
uvicorn 0.49.0 from C:\Users\10497\AppData\Local\Programs\Python\Python312\Lib\site-packages\uvicorn\__init__.py
```

并用 `py -m uvicorn knowledge.RESTfulAPI.lab:app --host 127.0.0.1 --port 8000` 启动服务，测试接口正常：

```bash
curl -s "http://127.0.0.1:8000/hello?name=FastAPI"
# {"message":"Hello, FastAPI!"}

curl -s -X POST "http://127.0.0.1:8000/echo" -H "Content-Type: application/json" -d '{"key":"value"}'
# {"key":"value"}
```

---

## 6. 额外提示：不要直接双击 / 脚本目录运行 lab.py

`lab.py` 里写了：

```python
uvicorn.run("knowledge.RESTfulAPI.lab:app", ...)
```

这种**模块路径字符串**要求项目根目录在 `sys.path` 中。如果你用 `python lab.py` 在脚本目录里运行，会报：

```
ModuleNotFoundError: No module named 'knowledge'
```

正确做法是：

```bash
# 在项目根目录 AIAgent 下执行
py -m uvicorn knowledge.RESTfulAPI.lab:app --host 127.0.0.1 --port 8000
```

或者使用 Anaconda：

```bash
python -m uvicorn knowledge.RESTfulAPI.lab:app --host 127.0.0.1 --port 8000
```

---

## 7. 如何避免以后再次踩坑

### 7.1 养成习惯：先确认解释器

```bash
python -c "import sys; print(sys.executable)"
```

### 7.2 为项目创建独立虚拟环境

最稳的做法是给项目建一个 `.venv`，所有依赖都装在里面：

```bash
# 在项目根目录
python -m venv .venv

# Windows 激活
.venv\Scripts\activate

# 安装依赖
pip install fastapi uvicorn
```

激活后，无论系统里有多少 Python，当前项目都只用 `.venv` 里的解释器和包。

---

## 8. 总结

- **报错原因**：Windows 上有多个 Python，`py` 默认指向的 Python.org 解释器没有安装 `fastapi`。
- **已执行修复**：`py -m pip install fastapi uvicorn`，现在 `py` 默认解释器也能导入并运行 FastAPI。
- **推荐运行方式**：在项目根目录使用 `py -m uvicorn knowledge.RESTfulAPI.lab:app --host 127.0.0.1 --port 8000`（或 Anaconda 的 `python -m uvicorn ...`）。

---

*生成时间：2026/06/29*  
*用途：AIAgent 项目实战课程问题排查记录*
