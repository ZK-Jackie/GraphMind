import os
from typing import Any

from tempfile import TemporaryDirectory

from pydantic import BaseModel, Field, model_validator

from graphmind.api.grpc.file_service import file_service_pb2_grpc, file_service_pb2


# GRPC 文件服务实现
class FileTransferServiceServicer(file_service_pb2_grpc.FileTransferServiceServicer):
    def upload(self, request_iterator, context):
        """
        上传文件块并合并文件
        Args:
            request_iterator: 文件块流，每一个元素是一个 FileIO 对象
            context: 上下文

        Returns:
            上传结果

        """
        return file_service_pb2.ServiceStatus(GrpcFileService().upload(request_iterator))

    def delete(self, request, context):
        """
        删除文件
        Args:
            request: 删除请求
            context: 上下文

        Returns:
            删除结果

        """
        return file_service_pb2.ServiceStatus(GrpcFileService().delete(request))


def _secure_filename(filename):
    """
    清理文件名，移除不安全的字符。
    """
    return filename.replace('/', '_').replace('..', '_')


class FileChunk(BaseModel):
    """
    文件块
    """
    content: bytes = Field(description="文件块内容")
    """文件块内容"""

    chunk_seq: int = Field(description="文件块序号", alias="chunkSeq")
    """文件块序号"""


class File(BaseModel):
    """
    文件
    """
    filename: str = Field(description="文件名")
    """文件名，带后缀"""

    file_size: int = Field(description="文件大小", alias="fileSize")
    """文件大小"""

    chunks: list[FileChunk] = Field(description="文件块列表")
    """文件块列表"""

    file_seq: int = Field(description="文件序号", alias="fileSeq")
    """文件序号"""

    chunk_total: int = Field(description="文件块总数", alias="chunkTotal")
    """文件块总数"""


class FileIO(BaseModel):
    """
    文件输入输出
    """
    task_id: str = Field(description="任务 ID", alias="taskId")
    """任务 ID"""

    total_file_size: int = Field(description="文件总大小", alias="totalFileSize")
    """文件总大小"""

    files: list[File] = Field(description="文件列表")
    """文件列表"""

    file_total: int = Field(description="文件总数", alias="fileTotal")
    """文件总数"""


class ServiceStatus(BaseModel):
    """
    上传状态
    """
    success: bool = Field(description="是否成功")
    """是否成功"""

    message: str = Field(description="消息")
    """消息"""


class DeleteRequest(BaseModel):
    """
    删除请求
    """
    task_id: str = Field(description="任务 ID", alias="taskId")
    """任务 ID"""

    filename: str = Field(description="文件名")
    """文件名"""


class GrpcFileService(BaseModel):
    """
    文件服务
    """
    upload_temp_dir: str | None = Field(description="上传临时目录", alias="uploadTempDir", default=None)
    """上传临时目录"""

    upload_save_dir: str | None = Field(description="上传保存目录", alias="uploadSaveDir", default=None)
    """上传保存目录"""

    @model_validator(mode="before")
    def validate_environment(cls, values: Any) -> Any:
        """
        验证环境变量
        Args:
            values: 参数

        Returns:
            values: 参数

        """
        values["upload_temp_dir"] = values["upload_temp_dir"] or os.getenv("UPLOAD_TEMP_DIR") or "/tmp/upload"
        values["upload_save_dir"] = values["upload_save_dir"] or os.getenv("UPLOAD_SAVE_DIR") or "/data/upload"
        return values

    def upload(self, iter_file_io) -> dict:
        """
        上传文件块并合并文件
        Args:
            iter_file_io: 文件块迭代器

        Returns:
            upload_status: 上传结果

        """
        try:
            # 创建临时目录保存文件块
            with TemporaryDirectory(dir=self.upload_temp_dir) as temp_dir:
                # 创建临时子目录，/tmp/upload
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir, exist_ok=True)
                # 1 保存文件块
                file_chunks_map = {}
                for file_io in iter_file_io:
                    task_id = file_io.taskId
                    total_file_size = file_io.fileSizes
                    # 遍历文件
                    for file in file_io.files:
                        # 清理文件名
                        file.filename = _secure_filename(file.filename)
                        file_key = (file.fileSeq, file.filename)
                        # 保存文件
                        if file_key not in file_chunks_map:
                            file_chunks_map[file_key] = []
                        # 遍历保存文件块
                        for chunk in file.chunks:
                            file_chunks_map[file_key].append((chunk.chunkSeq, chunk.content))

                # 2 合并文件块并保存
                for (file_seq, filename), chunks in sorted(file_chunks_map.items()):
                    chunks.sort()  # 每个文件的 chunk 都按 chunkSeq 排序
                    # 安全文件名
                    file_path = os.path.join(temp_dir, f"{task_id}_{file_seq}_{os.path.basename(filename)}")
                    with open(file_path, 'wb') as f:
                        for _, content in chunks:
                            f.write(content)

                # 3 成功上传，转移文件，保存路径为：/data/upload/{task_id}/{filename}
                for (file_seq, filename), _ in sorted(file_chunks_map.items()):
                    file_path = os.path.join(temp_dir, f"{task_id}_{file_seq}_{os.path.basename(filename)}")
                    save_path = os.path.join(self.upload_save_dir, task_id, filename)
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    os.rename(file_path, save_path)

            return ServiceStatus(
                success=True,
                message="Upload success"
            ).model_dump()
        except Exception as e:
            return ServiceStatus(
                success=False,
                message=f"Upload failed: {e}"
            ).model_dump()

    def delete(self, request) -> dict:
        """
        删除文件
        Args:
            request: 删除请求

        Returns:
            delete_status: 删除结果

        """
        py_request = DeleteRequest(**request)
        try:
            # 删除文件
            file_path = os.path.join(self.upload_save_dir, py_request.task_id, py_request.filename)
            os.remove(file_path)
            return ServiceStatus(
                success=True,
                message="Delete success"
            ).model_dump()
        except Exception as e:
            return ServiceStatus(
                success=False,
                message=f"Delete failed: {e}"
            ).model_dump()
