"""
Risk analizi: extraction çıktısını (SartnameOzeti) alıp teklif verenin
gözünden risklere çevirir.

Akış (extract_ozet'in kardeşi):
  SartnameOzeti → özeti metne çevir → Claude'a 'riske çevir' de (JSON)
               → Pydantic ile doğrula → RiskRaporu

LLM dışarıdan gelir (dependency injection).
"""
from __future__ import annotations

import json

from app.extraction.llm import LLMClient
from app.extraction.schema import SartnameOzeti
from app.risk.schema import RiskRaporu


def _json_temizle(metin: str) -> str:
    """LLM cevabındaki Markdown kod bloğu sarmalını temizler."""
    temiz = metin.strip()
    if temiz.startswith("```"):
        satirlar = temiz.split("\n")
        satirlar = satirlar[1:]
        satirlar = satirlar[:-1]
        temiz = "\n".join(satirlar)
    return temiz


def _prompt_kur(ozet: SartnameOzeti) -> str:
    """Risk analizi prompt'unu kurar: özeti ve risk şemasını Claude'a verir."""
    # Özeti JSON metnine çevir (Claude'a girdi olarak vereceğiz)
    ozet_json = ozet.model_dump_json(indent=2)
    # Risk şemasını otomatik üret (extract_ozet'teki gibi)
    risk_sema = json.dumps(RiskRaporu.model_json_schema(), ensure_ascii=False, indent=2)

    return (
        "Aşağıda bir kamu ihale şartnamesinin yapılandırılmış özeti var. "
        "Bunu, ihaleye teklif verecek bir firmanın gözünden RİSKLERE çevir.\n"
        "Her risk için: kategori (elenme/maliyet/nakit/süre), önem (yüksek/orta/düşük), "
        "açıklama, ve hangi bilgiye dayandığı (kaynak).\n"
        "Cevabını SADECE aşağıdaki JSON şemasına uygun ver. Markdown kullanma.\n\n"
        f"Risk şeması:\n{risk_sema}\n\n"
        f"İhale özeti:\n{ozet_json}"
    )


def risk_analiz_et(ozet: SartnameOzeti, llm: LLMClient) -> RiskRaporu:
    """
    Bir ihale özetini risk raporuna çevirir.

    Adımlar:
      1. Prompt'u kur (hazır: _prompt_kur)
      2. Claude'a gönder, cevabı al       <- SEN YAZ
      3. JSON'u temizle + RiskRaporu'ya doğrula, döndür   <- SEN YAZ
    """
    # 1. Prompt
    prompt = _prompt_kur(ozet)

    # 2. Claude'a gönder (SEN YAZ: cevabı 'ham_cevap' değişkenine al)
    ham_cevap = llm.complete(prompt)

    # 3. Temizle + doğrula + döndür (SEN YAZ)
    # İpucu: RiskRaporu.model_validate_json(_json_temizle(ham_cevap))
    return  RiskRaporu.model_validate_json(_json_temizle(ham_cevap))