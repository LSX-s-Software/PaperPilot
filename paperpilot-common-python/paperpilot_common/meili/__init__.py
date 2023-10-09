from django.conf import settings

MEILI_URL = settings.MEILI_URL if hasattr(settings, "MEILI_URL") else None

MEILI_MASTER_KEY = settings.MEILI_MASTER_KEY if hasattr(settings, "MEILI_MASTER_KEY") else None

if MEILI_URL:
    import meilisearch

    meili_client = meilisearch.Client(
        MEILI_URL,
        MEILI_MASTER_KEY,
    )

    try:
        from loguru import logger

        logger.success(f"MeiliSearch client connected to {MEILI_URL}")  # pragma: no cover
    except ImportError:
        import logging

        logger = logging.getLogger("meili")
        logger.info(f"MeiliSearch client connected to {MEILI_URL}")
