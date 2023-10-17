DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# DATABASES = DatabaseConfig.get()
DATABASES = {
    "default": {"ENGINE": "django.db.backends.dummy"},
}
