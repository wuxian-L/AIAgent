import sys
print(sys.executable)
from models import ChatMessage
import models
from config import settings
print(models.__file__)


req = ChatMessage(Id="session-123",Answer="你好")
print(req.model_dump())
print(req.model_dump(by_alias=True))
print(settings.dict())
#缺少必填 错误情况
try:
    ChatMessage()
except Exception as e:
    print(e)