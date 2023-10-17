from django.db import connections


def close_old_connections():
    for conn in connections.all():
        conn.close_if_unusable_or_obsolete()


def db_sync(func):
    """数据库连接关闭装饰器"""

    def func_wrapper(*args):
        close_old_connections()
        result = func(*args)
        return result

    return func_wrapper


def db(func):
    """数据库连接关闭装饰器"""

    async def func_wrapper(*args):
        close_old_connections()
        result = await func(*args)
        return result

    return func_wrapper
