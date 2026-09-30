"""
Extraction şeması (Pydantic modelleri).

Bunlar LLM'in dolduracağı 'formun alanları'. Key'ler sabit (biz belirledik),
değerleri LLM belgeden çıkaracak. Pydantic, LLM'in döndürdüğü JSON'u bu şemaya
karşı doğrulayıp güvenli bir Python nesnesine çevirir.

Not: Her alan 'str | None' — çünkü bilgi belgede bulunamayabilir. Bulunamazsa
None (yok), uydurma değil. Bu, projenin en kritik tasarım kararı.
"""
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
    """Bir şartnameden çıkarılan yapılandırılmış özet.

    Şimdilik birkaç temel alanla başlıyoruz; veri analizindeki tam şemaya
    (yeterlilik kriterleri, ceza maddeleri vb.) adım adım genişleteceğiz.
    """
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
