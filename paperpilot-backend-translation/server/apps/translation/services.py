from paperpilot_common.utils.log import get_logger

from server.business.baidu.translation import Translation


class TranslationService:
    logger = get_logger("translation.service")
    trans = Translation()

    async def translate(
        self, content: str, source_language: str, target_language: str
    ) -> str:
        if source_language == "":
            source_language = "auto"
        if target_language == "":
            target_language = "zh"

        self.logger.debug(
            f"translate {content} from {source_language} to {target_language}"
        )

        return await self.trans.translate(
            query=content,
            from_lang=source_language,
            to_lang=target_language,
        )


translation_service: TranslationService = TranslationService()
