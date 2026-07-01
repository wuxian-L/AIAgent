import sys
print(sys.executable)
from models import ChatMessage
import models
print(models.__file__)


req = ChatMessage(Id="session-123",Answer="你好")
print(req.model_dump())
print(req.model_dump(by_alias=True))

#缺少必填 错误情况
try:
    ChatMessage()
except Exception as e:
    print(e)