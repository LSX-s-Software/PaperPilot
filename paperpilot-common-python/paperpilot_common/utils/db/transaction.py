from asgiref.sync import sync_to_async
from django.db.transaction import Atomic


class AsyncAtomicContextManager(Atomic):
    def __init__(self, using=None, savepoint=True, durable=False):
        super().__init__(using, savepoint, durable)

    async def __aenter__(self):
        await sync_to_async(super().__enter__)()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await sync_to_async(super().__exit__)(exc_type, exc_value, traceback)


def aatomic(fun, *args, **kwargs):
    async def wrapper():
        async with AsyncAtomicContextManager():
            await fun(*args, **kwargs)

    return wrapper
