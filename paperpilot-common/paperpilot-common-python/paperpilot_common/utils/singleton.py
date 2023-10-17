from threading import RLock


class Singleton(type):
    """
    单例元类

    用法:
    >>> class A(metaclass=Singleton):
    >>>     pass
    """

    single_lock = RLock()

    def __call__(cls, *args, **kwargs):  # 创建cls的对象时候调用
        with Singleton.single_lock:
            if not hasattr(cls, "_instance"):
                cls._instance = super(Singleton, cls).__call__(*args, **kwargs)  # 创建cls的对象

        return cls._instance
