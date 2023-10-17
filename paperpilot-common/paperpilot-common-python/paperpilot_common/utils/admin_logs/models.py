"""
Django Admin Logs - Models.
"""
import json

from django.contrib.admin.models import LogEntryManager


class NoUserEntryManager(LogEntryManager):
    """The No User LogEntry Model Manager."""

    def __init__(self, model=None):
        super().__init__()
        self.model = model

    def log_action(
        self,
        user_id,
        content_type_id,
        object_id,
        object_repr,
        action_flag,
        change_message="",
    ):
        if isinstance(change_message, list):
            change_message = json.dumps(change_message)
        return self.model.objects.create(
            user_id=0,
            content_type_id=content_type_id,
            object_id=str(object_id),
            object_repr=object_repr[:200],
            action_flag=action_flag,
            change_message=change_message,
        )

    def get_queryset(self):
        return super().get_queryset()
