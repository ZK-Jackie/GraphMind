def _secure_filename(filename):
    """
    清理文件名，移除不安全的字符。
    """
    return filename.replace('/', '_').replace('..', '_')
