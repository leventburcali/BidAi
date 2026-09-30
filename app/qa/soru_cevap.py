
from __future__ import annotations

from app.common.models import ParsedArticle
from app.qa.embedding import EmbeddingClient
from app.qa.retrieval import en_yakin_maddeler
from app.extraction.llm import LLMClient


def _baglam_kur(maddeler: list[ParsedArticle]) -> str:
    """Bulunan maddeleri, Claude'a verilecek tek bir bağlam metnine çevirir."""
    parcalar = []
    for m in maddeler:
        parcalar.append(f"Madde {m.number} - {m.title}\n{m.body}")
    return "\n\n".join(parcalar)


def soru_cevapla(
    soru: str,
    maddeler: list[ParsedArticle],
    embedding: EmbeddingClient,
    llm: LLMClient,
    n: int = 3,
) -> tuple[str, list[ParsedArticle]]:
    """
    Belgeye dayanarak soruyu cevaplar (RAG).


    """
    # 1. Retrieval: en yakın maddeleri bul
    ilgili_maddeler = en_yakin_maddeler(maddeler, soru, embedding, n=n)

    # 2. Bağlam metnini kur
    baglam = _baglam_kur(ilgili_maddeler)

    prompt = ("Aşağıdaki şartname maddelerine dayanarak soruyu cevapla. Cevap maddelerde yoksa 'belgede bulunamadı' de, uydurma.\n\n"
            f"Maddeler: \n{baglam}\n\n"
            f"Soru: {soru}")

    cevap =  llm.complete(prompt)
    return cevap, ilgili_maddeler