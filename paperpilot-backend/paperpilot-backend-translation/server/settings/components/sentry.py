import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from server.settings.util import config

SENTRY_DSN = config("SENTRY_DSN", None)

SENTRY_ENABLE = config("SENTRY_ENABLE", False, bool)

if SENTRY_ENABLE:
    assert SENTRY_DSN, "SENTRY_DSN is required when SENTRY_ENABLE is True"
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
        ],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=0.05,
        debug=config("DEBUG", False),
        environment=config("DJANGO_ENV", "production"),
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
    )
