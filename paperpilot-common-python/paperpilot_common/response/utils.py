from paperpilot_common.response import ResponseType

response_type_enum: dict[str, "ResponseType"] | None = None


def get_response_type(code: str) -> "ResponseType":
    """
    根据状态码code取枚举

    :param code: 状态码code
    :return: 枚举
    """
    global response_type_enum

    if response_type_enum is None:
        response_type_enum = {e.value[0]: e for e in ResponseType if isinstance(e.value, tuple)}
    return response_type_enum[code]
