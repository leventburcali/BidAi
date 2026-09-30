
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict

class YeterlilikKriteri(BaseModel):
    tur: Optional[str] = None
    aciklama: Optional[str] = None
    oran: Optional[str] = None

class CezaMaddesi(BaseModel):
    tur: Optional[str] = None
    aciklama: Optional[str] = None
    oran: Optional[str] = None

class IdareBilgisi(BaseModel):
    adi: Optional[str] = None
    adresi: Optional[str] = None
    ikn: Optional[str] = None

class SartnameOzeti(BaseModel):

    model_config = ConfigDict(coerce_numbers_to_str=True)
    # İhale kimliği ve temel bilgiler
    ihale_konusu: Optional[str] = None        # işin adı / konusu
    ihale_usulu: Optional[str] = None         # "Açık ihale", "Pazarlık 21/e" vb.
    son_teklif_tarihi: Optional[str] = None   # ihale/teklif tarihi

    # Teminat
    gecici_teminat_orani: Optional[str] = None   # örn. "%3"
    kesin_teminat_orani: Optional[str] = None
    
    # Teklif koşulları
    teklif_gecerlilik_suresi: Optional[str] = None

    # Yeterlilik Kriterleri
    yeterlilik_kriterleri: list[YeterlilikKriteri] = []

    # Ceza Maddesi
    ceza_maddeleri: list[CezaMaddesi] = []

    # İdare Bilgisi
    idare_bilgisi: Optional[IdareBilgisi] = None
