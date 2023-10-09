from datetime import datetime, timedelta
from time import sleep
from typing import Any

import isodate
from meilisearch.models.task import Task as MeiliTask

from paperpilot_common.utils.meili.constant.task import TaskStatus, TaskType
from paperpilot_common.utils.meili.error import Error
from paperpilot_common.utils.meili.exceptions import MeiliSearchTaskFail, MeiliSearchTaskTimeoutError


class AsyncTask:
    uid: str
    index_uid: str | None
    status: TaskStatus
    type: TaskType
    details: dict[str, Any] | None
    error_dict: dict[str, str] | None
    canceled_by: int | None
    duration: timedelta | None
    enqueued_at: datetime | None
    started_at: datetime | None
    finished_at: datetime | None

    def __init__(self, task: MeiliTask):
        self.uid = task.uid
        self.index_uid = task.index_uid
        self.status = TaskStatus(task.status)
        self.type = TaskType(task.type)
        self.details = task.details
        self.error = task.error
        self.canceled_by = task.canceled_by
        self.duration = isodate.parse_duration(task.duration) if task.duration else None
        self.enqueued_at = isodate.parse_datetime(task.enqueued_at) if task.enqueued_at else None
        self.started_at = isodate.parse_datetime(task.started_at) if task.started_at else None
        self.finished_at = isodate.parse_datetime(task.finished_at) if task.finished_at else None

    @property
    def error(self) -> Error | None:
        return Error(self.error_dict) if self.error_dict else None

    @error.setter
    def error(self, error: dict[str, str] | None):
        self.error_dict = error

    @property
    def is_processing(self) -> bool:
        return self.status == TaskStatus.PROCESSING

    @property
    def is_enqueued(self) -> bool:
        return self.status == TaskStatus.ENQUEUED

    @property
    def is_failed(self) -> bool:
        return self.status == TaskStatus.FAILED

    @property
    def is_succeeded(self) -> bool:
        return self.status == TaskStatus.SUCCEEDED

    @property
    def is_canceled(self) -> bool:
        return self.status == TaskStatus.CANCELED

    @property
    def is_finished(self) -> bool:
        return self.is_succeeded or self.is_failed or self.is_canceled

    def wait(self, timeout: float = 5.0) -> "AsyncTask":
        """
        等待任务完成

        :param timeout: 超时时间
        :return:
        """
        start_time = datetime.now()
        while not self.is_finished:
            sleep(0.05)
            if (datetime.now() - start_time).seconds > timeout:
                raise MeiliSearchTaskTimeoutError("任务超时")

        if self.is_failed:
            raise MeiliSearchTaskFail(self.error)

        return self
