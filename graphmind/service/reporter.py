from abc import abstractmethod, ABC


from pydantic import BaseModel, Field

from graphmind.api.grpc.status_service_impl import report
from graphmind.service.base import ProcessStatus, ChatMessage


class BaseReporter(BaseModel, ABC):

    @staticmethod
    @abstractmethod
    def report(obj: BaseModel):
        pass


class GrpcReporter(BaseReporter):
    user_id: str | None = Field(description="User ID", alias="userId", default=None)
    """用户ID"""

    conv_id: str | None = Field(description="Chat ID", alias="convId", default=None)
    """对话ID"""

    user_message_id: str | None = Field(description="User message ID", alias="userMessageId", default=None)
    """处理的用户消息ID"""


    @staticmethod
    def report(obj: ProcessStatus) -> None:
        # 1 补充用户上下文信息
        obj.user_id = obj.user_id or GrpcReporter().user_id
        obj.conv_id = obj.conv_id or GrpcReporter().conv_id
        obj.user_message_id = obj.user_message_id or GrpcReporter().user_message_id
        # 2 发送状态信息
        # report(obj)
        print(obj.model_dump(by_alias=True))

    def load_context_from_message(self, message: ChatMessage):
        self.user_id = message.user_id
        self.conv_id = message.conv_id
        self.user_message_id = message.message_id
        return self
