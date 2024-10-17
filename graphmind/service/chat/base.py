import time
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel


class RoleEnum(Enum):
    """
    Role of the message sender
    """

    USER = 0
    """User"""

    AI = 1
    """AI"""


class ChatMessage(BaseModel):
    """
    接受来自 Java 端的用户信息，向 Java 端返回 AI 回答
    """

    role: int | None = Field(description="Role of the message sender", default=None)
    """消息发送者的角色，0 表示用户，1 表示机器人，建议用枚举类"""

    content: str | None = Field(description="Input & output message content", default=None)
    """输入或输出消息内容"""

    chunk_resp: bool | None = Field(description="Whether to invoke the chunk model", default=None)
    """是否分块传输回答，每一块都会是一个完整 json / ChatMessage 对象"""

    user_id: str | None = Field(description="User ID", default=None)
    """用户 ID，注意是 str 类型"""

    conv_id: str | None = Field(description="Chat ID", default=None)
    """对话 ID，注意是 str 类型"""

    message_id: str | None = Field(description="Message ID", default=None)
    """消息 ID，注意是 str 类型，本模块使用 uuid4 """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    """配置：可使用驼峰命名法序列化、可使用驼峰命名法反序列化"""


    def get_ai_message(self) -> "ChatMessage":
        return ChatMessage(
            role=RoleEnum.AI.value,
            content="",
            chunk_resp=False,
            user_id=self.user_id,
            conv_id=self.conv_id,
            message_id=str(uuid4())
        )


class StatusEnum(Enum):
    """
    Status of the message processing
    """

    UNPROCESSED = 0
    """状态信号：待处理"""

    PROCESSING = 1
    """状态信号：处理中"""

    PROCESSED = 2
    """状态信号：处理完成"""

    FAILED = 3
    """状态信号：回答处理失败"""

    TIMEOUT = 4
    """状态信号：回答处理超时"""

    CANCELLED = 5
    """状态信号：被取消"""

    START = 11
    """控制信号：开始"""

    CONTINUE = 12
    """控制信号：继续"""

    PAUSE = 13
    """控制信号：暂停"""

    STOP = 14
    """控制信号：停止"""


class ChatStatus(BaseModel):
    """
    由 AI 端向 Java 端单向传输的状态汇报消息
    """

    user_id: str | None = Field(description="User ID", default=None)
    """用户ID"""

    conv_id: str | None = Field(description="Chat ID", default=None)
    """对话ID"""

    user_message_id: str | None = Field(description="User message ID", default=None)
    """处理的用户消息ID"""

    status_id: int | None = Field(description="Status ID", default=None)
    """当前处理状态ID，0-未处理，1-处理中，2-处理完成"""

    status_message: str | None = Field(description="Status message", default=None)
    """当前处理状态消息"""

    send_time: str | None = Field(description="Send time", default=None)
    """当前处理状态信号发送时间，即发送信息的这个状态的开始时间，也是上一个状态的结束时间"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    """配置：可使用驼峰命名法序列化、可使用驼峰命名法反序列化"""

    @staticmethod
    def from_user_message(user_message: ChatMessage,
                          status_id: int,
                          status_message: str,
                          send_time: str = str(time.time())) -> "ChatStatus":
        return ChatStatus(
            user_id=user_message.user_id,
            conv_id=user_message.conv_id,
            user_message_id=user_message.message_id,
            status_id=status_id,
            status_message=status_message,
            send_time=send_time
        )
