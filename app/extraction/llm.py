"""
LLM istemci arayüzü ve test için sahte implementasyonu.

Buradaki fikir (bağımlılığı soyutlama):
  Extraction mantığımız "bir LLM istemcisi" ile konuşur, ama bu istemcinin
  GERÇEKTEN Claude mı yoksa test için sahte bir nesne mi olduğunu bilmez.
  Böylece:
    - Mantığı gerçek API'ye (para + internet) ihtiyaç duymadan test edebiliriz.
    - Sağlayıcı değişirse (OpenAI -> Claude) sadece tek bir sınıfı değiştiririz.

Java karşılığı: 'interface LLMClient' + farklı 'implements' sınıfları.
"""
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
    """
    Test için sahte LLM. Gerçek modele bağlanmaz; kendisine önceden verilen
    cevabı aynen döndürür. Böylece 'model şöyle cevap verirse kodum ne yapar?'
    senaryolarını kontrollü biçimde test ederiz.

    Not: LLMClient(Protocol)'dan açıkça miras almasına gerek yok — 'complete'
    metodunu taşıdığı için Python onu otomatik olarak uygun kabul eder
    (buna 'duck typing' denir: ördek gibi yürüyorsa ördektir).
    """

    def __init__(self, canned_response: str):
        self.canned_response = canned_response  # önceden ayarlanan cevap
        self.last_prompt: str | None = None  # en son hangi prompt geldi (testte işe yarar)

    def complete(self, prompt: str) -> str:
        self.last_prompt = prompt
        return self.canned_response
