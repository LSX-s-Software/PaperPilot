from paperpilot_common.utils.meili.constant.error import ErrorType


class Error:
    message: str
    code: str
    type: ErrorType
    link: str

    def __init__(self, error: dict[str, str]):
        self.message = error["message"]
        self.code = error["errorCode"]
        self.type = ErrorType(error["errorType"])
        self.link = error["errorLink"]
