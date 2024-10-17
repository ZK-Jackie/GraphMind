import functools


def log_report(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"开始执行 {func.__name__}")
        result = func(*args, **kwargs)  # 执行原函数
        print(f"{func.__name__} 执行完毕")
        return result

    return wrapper