from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class Risk(BaseModel):
    """Bir ihale riski: teklif verenin dikkat etmesi gereken bir nokta."""
    kategori: Optional[str] = None
    onem: Optional[str] = None
    aciklama: Optional[str] = None
    kaynak: Optional[str] = None

class RiskRaporu(BaseModel):
    """Bir ihalenin tüm risk analizi."""
    riskler: list[Risk] = []
    genel_degerlendirme: Optional[str] = None   # opsiyonel özet yorum