"""
BidAi API — FastAPI sunum katmanı.

Çalıştırmak için (proje kökünde):
    uvicorn app.api.main:app --reload

Adresler:
    http://127.0.0.1:8000/health   -> sağlık kontrolü
    http://127.0.0.1:8000/docs     -> otomatik API dokümantasyonu (Swagger)
"""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()
from app.risk.analiz import risk_analiz_et
from app.risk.schema import RiskRaporu
from app.extraction.claude_client import ClaudeLLMClient
from app.extraction.ozet_extractor import extract_ozet
from app.extraction.schema import SartnameOzeti
from fastapi import FastAPI, UploadFile, File, Form
from app.parsing.parser import parse_document
from app.qa.embedding import LocalEmbeddingClient
from app.qa.soru_cevap import soru_cevapla
import tempfile
import os
from fastapi import HTTPException
from fastapi import Depends

app = FastAPI(
    title="BidAi",
    description="Kamu ihale şartnamesi analiz asistanı",
    version="0.1.0",
)


# --- Request modelleri (gelen verinin şeması) ---


class OzetIstegi(BaseModel):
    """POST /ozet'e gelen veri: bir belge metni."""
    belge_metni: str

def get_claude() -> ClaudeLLMClient:
    """Claude istemcisini sağlar. Her istekte yeni bir tane (hafif, sorun değil)."""
    return ClaudeLLMClient()


_embedding_instance = None


def get_embedding() -> LocalEmbeddingClient:
    """Embedding istemcisini sağlar — ilk çağrıda yükler, sonra tekrar kullanır."""
    global _embedding_instance
    if _embedding_instance is None:
        _embedding_instance = LocalEmbeddingClient()
    return _embedding_instance

@app.get("/health")
def health():
    """Sağlık kontrolü: API ayakta mı?"""
    return {"status": "ok"}


@app.post("/ozet", response_model=SartnameOzeti)
def ozet_cikar(istek: OzetIstegi, claude: ClaudeLLMClient = Depends(get_claude)) -> SartnameOzeti:
    """Bir şartname metninden yapılandırılmış özet çıkarır."""
    # Claude istemcisini oluştur
    if not istek.belge_metni or len(istek.belge_metni.strip()) < 50:
        raise HTTPException(
            status_code=422,
            detail="Belge metni boş veya çok kısa (en az 50 karakter gerekli).",
        )
    try:

        ozet = extract_ozet(istek.belge_metni, claude)
        return ozet
    except HTTPException:
        raise  # HTTPException'ı olduğu gibi geçir (yukarıdaki 422 gibi)
    except Exception as e:
        # Beklenmedik hata (Claude hatası, JSON hatası vs.)
        raise HTTPException(
            status_code=500,
            detail=f"Özet çıkarılırken hata oluştu: {str(e)}",
        )

class RiskIstegi(BaseModel):
    """POST /risk'e gelen veri: bir belge metni."""
    belge_metni: str

@app.post("/risk", response_model=RiskRaporu)
def risk_analizi(istek: RiskIstegi , claude: ClaudeLLMClient = Depends(get_claude)) -> RiskRaporu:
    """Bir şartname metninden risk raporu üretir."""
    if not istek.belge_metni or len(istek.belge_metni.strip()) < 50:
        raise HTTPException(
            status_code=422,
            detail="Belge metni boş veya çok kısa (en az 50 karakter gerekli).",
        )
    try:
        ozet = extract_ozet(istek.belge_metni, claude)
        rapor = risk_analiz_et(ozet, claude)
        return rapor
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk analizi sırasında hata: {str(e)}")


@app.post("/soru")
def soru_sor(dosya: UploadFile = File(...), soru: str = Form(...), claude: ClaudeLLMClient = Depends(get_claude), embedding: LocalEmbeddingClient = Depends(get_embedding)):
    """Bir şartname dosyası yükle + soru sor; belgeye dayalı cevap al (RAG)."""
    if not soru or len(soru.strip()) < 3:
        raise HTTPException(status_code=422, detail="Soru boş veya çok kısa.")
    
    uzanti = os.path.splitext(dosya.filename)[1]  # ".doc" gibi
    with tempfile.NamedTemporaryFile(delete=False, suffix=uzanti) as tmp:
        tmp.write(dosya.file.read())  # yüklenen içeriği geçici dosyaya yaz
        gecici_yol = tmp.name


    try:
        doc = parse_document(gecici_yol)

        if not doc.articles:
            raise HTTPException(
                status_code=422,
                detail="Bu belge işlenemedi. Desteklenen belgeler: yapım işi idari şartnamesi ve sözleşme tasarısı. Teknik şartnameler ve taranmış PDF'ler henüz desteklenmiyor.",
            )

        cevap, kaynaklar = soru_cevapla(soru, doc.articles, embedding, claude)


        return {
           "soru": soru,
           "cevap": cevap,
           "kaynaklar": [f"Madde {m.number} - {m.title}" for m in kaynaklar],
        }
    finally:
        os.remove(gecici_yol)