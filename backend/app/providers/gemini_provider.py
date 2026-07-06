# gemini_provider.py
# Purpose: Google Gemini LLM API provider integration.
# Responsibilities:
#   - Generate text generations using Gemini 1.5 Flash
#   - Generate text embedding vectors using models/embedding-001
# DO NOT: Hardcode API keys (read from settings.GEMINI_API_KEY).
# DO NOT: Bypass abstract interface method definitions.

import logging
import anyio
import google.generativeai as genai

from app.core.config import settings
from app.core.constants import GEMINI_FLASH_MODEL, GEMINI_EMBEDDING_MODEL
from app.core.exceptions import ProviderException
from app.providers.base_provider import BaseProvider, ProviderResponse

logger = logging.getLogger(__name__)


class GeminiProvider(BaseProvider):
    """Google Gemini LLM and Embedding API Provider."""

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY or "mock_key")
        self.model_name = GEMINI_FLASH_MODEL
        self.embed_model_name = GEMINI_EMBEDDING_MODEL

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> ProviderResponse:
        logger.info(f"Generating content with Gemini model: {self.model_name}")
        try:
            config = genai.GenerationConfig(
                temperature=0.2,
            )
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=config,
                system_instruction=system_prompt
            )

            # Run blocking API call in executor thread to prevent event loop starvation
            response = await anyio.to_thread.run_sync(model.generate_content, prompt)

            tokens = None
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                tokens = response.usage_metadata.total_token_count

            return ProviderResponse(
                content=response.text,
                model=self.model_name,
                provider="gemini",
                tokens_used=tokens
            )
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise ProviderException(f"Gemini generation failure: {str(e)}")

    async def embed(self, text: str) -> list[float]:
        logger.debug(f"Generating embedding for text using model: {self.embed_model_name}")
        try:
            # Run blocking API call in executor thread to prevent event loop starvation
            response = await anyio.to_thread.run_sync(
                lambda: genai.embed_content(
                    model=self.embed_model_name,
                    content=text,
                    task_type="retrieval_document"
                )
            )
            return response.get("embedding", [])
        except Exception as e:
            logger.error(f"Gemini embedding call failed: {e}")
            raise ProviderException(f"Gemini embedding failure: {str(e)}")
