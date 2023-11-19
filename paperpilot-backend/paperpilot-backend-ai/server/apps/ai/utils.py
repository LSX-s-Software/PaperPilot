from paperpilot_common.protobuf.ai.ai_pb2 import FinishReason


def get_finish_reason_enum(status: str | None) -> FinishReason:
    if status == "" or status is None:
        return FinishReason.NULL
    elif status == "stop":
        return FinishReason.STOP
    elif status == "length":
        return FinishReason.LENGTH
    elif status == "function_call":
        return FinishReason.FUNCTION_CALL
    elif status == "content_filter":
        return FinishReason.CONTENT_FILTER

    return FinishReason.NULL
