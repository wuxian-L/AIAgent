from pydantic import BaseModel,Field
from typing import Optional

class ChatMessage(BaseModel):
    session_id:str = Field(...,description = "会话ID",alias = "Id")
    answer:str = Field(...,description="AI回答",alias = "Answer")

    model_config = {
        "populate_by_name" : True,
        "json_schema_extra":{
            "example":{
                "Id":"123",
                "Answer":"你好"
            }
        }
    }

