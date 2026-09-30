
from __future__ import annotations

from app.extraction.llm import LLMClient
from app.extraction.schema import SartnameOzeti


def _prompt_kur(belge_metni: str) -> str:
    """LLM'e gönderilecek prompt'u kurar: şemayı tanıtır, JSON ister."""
    import json
    sema = json.dumps(SartnameOzeti.model_json_schema(), ensure_ascii=False, indent=2)
    return (
        "Aşağıdaki ihale şartnamesi metninden bilgileri çıkar.\n"
        "Cevabını, TAM OLARAK aşağıdaki JSON şemasına uygun geçerli JSON olarak ver.\n"
        "Kurallar:\n"
        "- Sadece JSON döndür, Markdown kod bloğu veya ters tırnak kullanma.\n"
        "- Tüm değerler metin (string) olmalı; sayıları birimiyle ver (örn: \"%3\", \"180 gün\").\n"
        "- Bilgi belgede yoksa o alanı null bırak, uydurma.\n"
        "- 'array' tipindeki alanları mutlaka liste olarak ver, düz metin değil.\n\n"
        f"JSON şeması:\n{sema}\n\n"
        f"Şartname metni:\n{belge_metni}"
    )


def extract_ozet(belge_metni: str, llm: LLMClient) -> SartnameOzeti:
    """
    Belge metninden yapılandırılmış özet çıkarır.


    """
    # 1. Prompt
    prompt = _prompt_kur(belge_metni)


    ham_cevap = llm.complete(prompt)


    #    model_validate_json: JSON metnini alır, şemaya karşı doğrular, nesne döndürür.
    ozet = SartnameOzeti.model_validate_json(_json_temizle(ham_cevap))
    return ozet

def _json_temizle(metin:str) -> str:
    temiz = metin.strip()
    if temiz.startswith("```"):
        satirlar = temiz.split("\n")
        satirlar = satirlar[1:]
        satirlar = satirlar[:-1]
        temiz = "\n".join(satirlar)
    return temiz
