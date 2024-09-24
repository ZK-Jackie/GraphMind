from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: int | None = Field(description="Role of the message sender", default=None)
    """消息发送者的角色，0表示用户，1表示机器人"""

    content: str | None = Field(description="Input & output message content", default=None)
    """输入或输出消息内容"""

    chunk_resp: bool | None = Field(description="Whether to invoke the chunk model", default=None)
    """是否分块传输回答"""

    user_id: str | None = Field(description="User ID", default=None)
    """用户ID"""

    conv_id: str | None = Field(description="Chat ID", default=None)
    """对话ID"""

    message_id: str | None = Field(description="Message ID", default=None)
    """消息ID，用于唯一标识每一条消息，使用uuid4"""