from paperpilot_common.utils.log import get_logger

from server.settings.components.configs import DatabaseConfig

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASES = DatabaseConfig.get()

logger = get_logger("settings.db")

logger.success(
    f"Database connect to: {DATABASES['default']['HOST'] or 'sqlite'}"
)
