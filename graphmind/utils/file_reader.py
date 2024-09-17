import os

def find_file(file: str | list[str],
              allowed_type: str | list[str]) -> list[str]:
    """
    预处理 file 字段，首先确保其为文件路径或目录路径（列表），最后将其转换为具体的文件路径列表
    Args:
        file: 文件路径或目录路径（列表）
        allowed_type: 允许的文件类型
    Returns: 文件路径列表
    """
    # 处理文件路径
    if isinstance(file, str):
        # 两种情况：文件路径或目录路径
        if _check_isfile(file):
            file = [file]
        elif _check_isdir(file):
            file_list = []
            _list_files(file, file_list, allowed_type)
            if file_list:
                file = file_list
            else:
                raise FileNotFoundError(f"No file was found in: {file}")
        else:
            raise FileNotFoundError(f"File not found: {file}")
    elif isinstance(file, list):
        for f in file:
            if not os.path.isfile(f):
                raise FileNotFoundError(f"File not found: {f}")
    else:
        raise ValueError(f"Invalid file param: {file}")

    return file

def _check_isdir(path) -> bool:
    """
    检查是否是目录
    Args:
        path: 文件路径
    Returns: 是否是目录
    """
    return os.path.isdir(path)


def _check_isfile(path) -> bool:
    """
    检查是否是文件
    Args:
        path: 文件路径
    Returns: 是否是文件
    """
    return os.path.isfile(path)


def _list_files(directory, file_list, file_type=None) -> None:
    """
    遍历指定目录下的所有文件和子目录，将文件路径添加到列表中
    Args:
        directory:  目录路径
        file_list:  文件路径列表，用于存储文件路径，由用户传入，最终返回
        file_type:  允许的文件类型
    Returns: None
    """
    # 遍历指定目录下的所有文件和子目录
    for item in os.listdir(directory):
        # 拼接完整的文件或目录路径
        path = os.path.join(directory, item)
        # 如果是目录，递归调用list_files函数
        if _check_isdir(path):
            _list_files(path, file_list)
        # 如果是文件，将路径添加到列表中
        else:
            if not file_type:
                file_list.append(path)
            else:
                if path.split(".")[-1] in file_type:
                    file_list.append(path)