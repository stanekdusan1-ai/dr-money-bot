from __future__ import annotations
from openai import OpenAI
from app.core.config import get_settings


class LLMClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = (
            OpenAI(api_key=self.settings.openai_api_key, base_url=self.settings.openai_base_url)
            if self.settings.openai_api_key
            else None
        )

    def complete(self, system: str, user: str, fallback: str) -> str:
        if not self.client:
            return fallback
        try:
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[{'role': 'system', 'content': system}, {'role': 'user', 'content': user}],
                temperature=0.4,
            )
            return response.choices[0].message.content or fallback
        except Exception as exc:
            return f'{fallback}\n\n[Hinweis: OpenAI-Aufruf fehlgeschlagen: {exc}]'
