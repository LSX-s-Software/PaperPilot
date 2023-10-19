from django.conf import settings

SCIHUB_BASE_URL = getattr(settings, "SCIHUB_BASE_URL", "https://sci-hub.se")
