"""
Risk analizi testleri — sahte LLM ile fonksiyonun mekaniğini doğrular.
Sahte LLM'e hazır bir risk JSON'u verdirip, fonksiyonun onu doğru
RiskRaporu nesnesine çevirdiğini test ederiz.
"""
from app.extraction.llm import FakeLLMClient
from app.extraction.schema import SartnameOzeti
from app.risk.analiz import risk_analiz_et
from app.risk.schema import Risk


# Sahte LLM'in döndüreceği hazır risk JSON'u
SAHTE_RISK_JSON = """{
  "riskler": [
    {"kategori": "elenme", "onem": "yüksek", "aciklama": "İş deneyimi şartı yüksek", "kaynak": "Madde 7"},
    {"kategori": "nakit", "onem": "orta", "aciklama": "Kesin teminat %6", "kaynak": "Madde 45"}
  ],
  "genel_degerlendirme": "Riskli ihale"
}"""


def test_risk_raporu_doner():
    """risk_analiz_et, JSON'dan RiskRaporu nesnesi üretmeli."""
    fake_llm = FakeLLMClient(canned_response=SAHTE_RISK_JSON)
    ozet = SartnameOzeti(ihale_konusu="test ihalesi")  # basit bir özet

    rapor = risk_analiz_et(ozet, fake_llm)


    assert len(rapor.riskler) == 2
    assert rapor.genel_degerlendirme == "Riskli ihale"
    for riskler in rapor.riskler:
        assert isinstance(riskler, Risk)

def test_markdown_sarmali_temizlenir():
    """Claude JSON'u ```json ile sararsa bile temizlenip parse edilmeli."""
    sarmalanmis = "```json\n" + SAHTE_RISK_JSON + "\n```"
    fake_llm = FakeLLMClient(canned_response=sarmalanmis)
    ozet = SartnameOzeti(ihale_konusu="test")

    rapor = risk_analiz_et(ozet, fake_llm)

    # SEN YAZ: Markdown sarmalına rağmen 2 risk parse edilmeli
    assert len(rapor.riskler) == 2