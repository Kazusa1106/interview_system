"""Message schemas"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


class MessageCreate(BaseModel):
    text: str = Field(
        ..., min_length=1, description="用户输入文本", examples=["我认为最重要的是……"]
    )


class MessageResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "msg_abc123",
                "role": "assistant",
                "content": "请描述一下您的教学理念",
                "timestamp": 1705392000000,
            }
        }
    )

    id: str
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., description="消息内容")
    timestamp: int = Field(..., description="毫秒时间戳")
