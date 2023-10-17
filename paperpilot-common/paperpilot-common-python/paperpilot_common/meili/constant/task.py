from django.db import models


class TaskStatus(models.TextChoices):
    """
    任务状态
    """

    ENQUEUED = "enqueued", "排队中"
    PROCESSING = "processing", "处理中"
    SUCCEEDED = "succeeded", "成功"
    FAILED = "failed", "失败"
    CANCELED = "canceled", "已取消"


class TaskType(models.TextChoices):
    """
    任务类型
    """

    INDEX_CREATION = "indexCreation", "创建索引"
    INDEX_UPDATE = "indexUpdate", "更新索引"
    INDEX_DELETION = "indexDeletion", "删除索引"
    INDEX_SWAP = "indexSwap", "交换索引"

    DOCUMENT_ADDITION_OR_UPDATE = "documentAdditionOrUpdate", "添加或更新文档"
    DOCUMENT_DELETION = "documentDeletion", "删除文档"

    SETTINGS_UPDATE = "settingsUpdate", "更新设置"

    DUMP_CREATION = "dumpCreation", "创建备份"

    TASK_CANCELLATION = "taskCancelation", "取消任务"
    TASK_DELETION = "taskDeletion", "删除任务"

    SNAPSHOT_CREATION = "snapshotCreation", "创建快照"
