from django.contrib.admin.models import LogEntry


def custom_render(self, context):
    entries = LogEntry.objects.all()
    context[self.varname] = entries.select_related("content_type")[: int(self.limit)]
    return ""
