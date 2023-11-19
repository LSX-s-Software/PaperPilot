import uuid
from contextvars import ContextVar
from uuid import UUID

trace_id_context: ContextVar[UUID] = ContextVar("trace_id", default=UUID(int=0))


def get_trace_id() -> UUID:
    """
    获取trace_id
    """
    trace_id = trace_id_context.get()
    if trace_id is None:
        trace_id = uuid.uuid4()
    return trace_id
