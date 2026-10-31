import os
from dotenv import load_dotenv

from app.extraction.claude_client import ClaudeLLMClient
from app.risk.analiz import risk_analiz_et

load_dotenv()
from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from app.extraction import ozet_extractor

@tool()
def teminat_hesapla(teklif_bedeli:float, oran_yuzde: float) -> float:
    """teklif bedeli ve yüzde oran verildiğinde teminat tutarını hesaplar"""

    return  teklif_bedeli*oran_yuzde/100

@tool()
def ozet_cikar(belge_metni:str) -> str:
    """Belge metninin ikn, yeterlilik, süre gibi maddelerini kullanıcıya sunan yapılandılırmış özeti."""
    llm = ClaudeLLMClient()
    ozet = ozet_extractor.extract_ozet(belge_metni, llm)
    return ozet.model_dump_json()

@tool()
def risk_analiz(belge_metni:str)->str:
    """Belgenin yapılandırılmış özetine dayanarak elenme, maliyet, nakit akışı, süre riskleri gibi risk unsurlarını çıkarır."""

    llm = ClaudeLLMClient()
    ozet = ozet_extractor.extract_ozet(belge_metni, llm)
    rapor = risk_analiz_et(ozet, llm)
    return rapor.model_dump_json()


class Danisman:

    def __init__(self, model: str= "claude-haiku-4-5"):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY bulunamadı. Anahtarı .env dosyasına ekleyin.")

        llm = ChatAnthropic(model=model, temperature=0)

        self.agent = create_react_agent(llm, [teminat_hesapla,ozet_cikar, risk_analiz])


    def sor(self, soru:str)->str:

        answer = self.agent.invoke({"messages": [{"role": "user", "content": soru}]})

        return answer["messages"][-1].content


if __name__ == "__main__":
    d = Danisman()
    sartname = """KAMU İHALE İDARİ ŞARTNAMESİ

İhale Kayıt Numarası (İKN): 2026/1478562
İdarenin Adı: T.C. Sağlık Bakanlığı Ankara İl Sağlık Müdürlüğü
İşin Adı: 12 (on iki) aylık malzemeli genel temizlik hizmeti alımı
İhale Usulü: Açık ihale usulü (4734 sayılı Kanun 19. madde)

Tekliflerin Geçerlilik Süresi: İhale tarihinden itibaren 90 (doksan) takvim günüdür.
Geçici Teminat: İstekliler teklif ettikleri bedelin %3'ünden az olmamak üzere geçici teminat vereceklerdir.
Kesin Teminat: İhale bedelinin %6'sı oranında kesin teminat alınır.

İş Deneyim Belgesi: Son 5 yıl içinde teklif edilen bedelin %25'inden az olmamak üzere tek sözleşmeye ilişkin iş deneyimi.
Kalite Belgesi: İstekliler ISO 9001 Kalite Yönetim Sistemi belgesini"""
    soru = (
            "Bu şartnameyi benim için değerlendir: kısa bir özet çıkar, "
            "en önemli riskleri söyle, ve teklif bedelim 2.000.000 TL olursa "
            "geçici teminat tutarı ne olur?\n\n" + sartname
    )
    print(d.sor(soru))