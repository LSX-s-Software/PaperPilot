from django.db import models as django_models
from django.db.models.signals import class_prepared


def override_field(sender, **kwargs):
    if sender.__name__ == "LogEntry":
        user_id = django_models.IntegerField(default=0, verbose_name="user")
        sender._meta.local_fields = [f for f in sender._meta.fields if f.name not in ["user"]]
        user_id.contribute_to_class(sender, "user_id")


class_prepared.connect(override_field)
