"""
Extraction mantığı: madde metninden yapılandırılmış bilgi çıkarma.

Şimdilik tek bir alanla başlıyoruz (geçici teminat oranı), mantığı oturtmak için.
Sonra bunu şemaya (birden çok alan) genişleteceğiz.

Önemli tasarım: LLM 'dışarıdan' parametre olarak gelir (dependency injection).
Böylece testte sahte, gerçekte Claude verilebilir; fonksiyon farkı bilmez.
"""
from __future__ import annotations

from app.extraction.llm import LLMClient


def extract_teminat_orani(madde_metni: str, llm: LLMClient) -> str:

    prompt = (
        "Aşağıdaki ihale şartnamesi maddesinden geçici teminat oranını çıkar. "
        "Sadece oranı döndür (örnek: %3), başka açıklama ekleme. "
        "Metinde oran yoksa 'bulunamadı' yaz.\n\n"
        f"Madde metni:\n{madde_metni}"
        
    )

    response = llm.complete(prompt)
    return response

