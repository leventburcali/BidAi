"""
Gerçek Claude implementasyonu (LLMClient arayüzüne uyar).

FakeLLMClient testler için sahte cevap veriyordu; bu sınıf ise complete()'i
gerçekten Claude'a bağlar. Arayüz aynı olduğu için extraction kodunun hiçbir
yeri değişmez — sahte yerine bunu verirsiniz, gerisi aynı çalışır.

GÜVENLİK: API anahtarı KODA yazılmaz. Ortam değişkeninden (ANTHROPIC_API_KEY)
okunur. Böylece kod paylaşılsa bile anahtar sızmaz.

Kurulum (kendi ortamınızda):
    pip install anthropic
    # Anahtarı ortam değişkeni olarak ayarlayın:
    #   Mac/Linux:  export ANTHROPIC_API_KEY="sk-ant-..."
    #   (kalıcı için ~/.zshrc veya ~/.bashrc'ye ekleyin)
"""
from __future__ import annotations

import os


class ClaudeLLMClient:
    """LLMClient arayüzünü gerçek Claude ile karşılayan implementasyon."""

    def __init__(self, model: str = "claude-haiku-4-5"):

        from anthropic import Anthropic

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY ortam değişkeni bulunamadı. "
                "Anahtarınızı ayarlayın: export ANTHROPIC_API_KEY='sk-ant-...'"
            )

        self.client = Anthropic(api_key=api_key)
        self.model = model


    def complete(self, prompt: str) -> str:
        """Prompt'u Claude'a gönderir, metin cevabını döndürür."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text