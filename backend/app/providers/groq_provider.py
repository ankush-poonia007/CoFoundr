# groq_provider.py
# Purpose: Groq API LLM provider integration.
# Responsibilities:
#   - Generate text generations using Groq Llama3 model
# DO NOT: Hardcode API keys (read from settings.GROQ_API_KEY).
# DO NOT: Attempt to run embeddings via Groq (raise ProviderException).

import logging
import anyio
from groq import Groq

from app.core.config import settings
from app.core.constants import GROQ_MODEL
from app.core.exceptions import ProviderException
from app.providers.base_provider import BaseProvider, ProviderResponse

logger = logging.getLogger(__name__)


class GroqProvider(BaseProvider):
    """Groq LLM API Provider."""

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY or "mock_key")
        self.model_name = GROQ_MODEL

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> ProviderResponse:
        logger.info(f"Generating content with Groq model: {self.model_name}")
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            # Run blocking API call in executor thread to prevent event loop starvation
            chat_completion = await anyio.to_thread.run_sync(
                lambda: self.client.chat.completions.create(
                    messages=messages,
                    model=self.model_name,
                    temperature=0.2,
                )
            )

            content = chat_completion.choices[0].message.content or ""
            tokens = chat_completion.usage.total_tokens if chat_completion.usage else None

            return ProviderResponse(
                content=content,
                model=self.model_name,
                provider="groq",
                tokens_used=tokens
            )
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            raise ProviderException(f"Groq generation failure: {str(e)}")

    async def embed(self, text: str) -> list[float]:
        """Groq does not support embeddings; always raises ProviderException."""
        raise ProviderException("Groq provider does not support text embedding. Use Gemini provider instead.")
