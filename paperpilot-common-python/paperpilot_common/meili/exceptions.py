from meilisearch.errors import MeiliSearchError

from paperpilot_common.utils.meili.error import Error


class MeiliSearchTaskError(MeiliSearchError):
    """
    MeiliSearch 异步任务错误
    """

    def __str__(self):
        return f"MeiliSearchTaskError, {self.message}"


class MeiliSearchTaskTimeoutError(MeiliSearchError):
    """
    MeiliSearch 异步任务超时错误
    """

    def __str__(self):
        return f"MeiliSearchTaskTimeoutError, {self.message}"


class MeiliSearchTaskFail(MeiliSearchError):
    """
    MeiliSearch 异步任务失败
    """

    def __init__(self, error: Error):
        super().__init__(error.message)
        self.error = error

    def __str__(self):
        return f"MeiliSearchTaskPendingError, {self.message}"
