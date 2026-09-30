
from __future__ import annotations

from typing import Protocol


class LLMClient(Protocol):
    """
    Bir LLM istemcisinin uyması gereken sözleşme (interface).
    'Protocol' = Python'un interface yazma biçimi. Bu sözleşmeye uyan
    HER sınıf (gerçek ya da sahte) extraction tarafından kullanılabilir.

    Sözleşme tek bir metot: bir prompt (metin) al, bir cevap (metin) döndür.
    """

    def complete(self, prompt: str) -> str:
        """Verilen prompt'a karşılık modelin metin cevabını döndürür."""
        ...


class FakeLLMClient:


    def __init__(self, canned_response: str):
        self.canned_response = canned_response
        self.last_prompt: str | None = None

    def complete(self, prompt: str) -> str:
        self.last_prompt = prompt
        return self.canned_response
