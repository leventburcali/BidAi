import os
from dotenv import load_dotenv

from app.extraction.claude_client import ClaudeLLMClient
from app.risk.analiz import risk_analiz_et
from app.qa.chroma_store import sorgula, indexle

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
        from app.api.main import get_embedding
        self.llm = ChatAnthropic(model=model, temperature=0)

        self.embedding = get_embedding()


    def degerlendir(self, articles, soru:str)->str:
        col = indexle(articles, self.embedding)
        madde_ara = madde_ara_yap(col, self.embedding)
        agent = create_react_agent(self.llm, [teminat_hesapla, ozet_cikar,risk_analiz,madde_ara])
        sonuc = agent.invoke({"messages": [{"role": "user", "content": soru}]})
        return sonuc["messages"][-1].content

def madde_ara_yap(col, embedding):
    @tool
    def madde_ara(soru: str) -> str:
        """ belgede soruya en ilgili maddeleri bulup döndürür"""
        sonuc = sorgula(col, soru, embedding)
        return "\n\n".join(sonuc)
    return madde_ara
