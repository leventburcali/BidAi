"""
soru_cevapla testleri — sahte LLM + sahte embedding ile RAG akışının
MEKANİĞİNİ doğrular (gerçek Claude/embedding'e gitmeden).
"""
from app.common.models import ParsedArticle
from app.qa.embedding import FakeEmbeddingClient
from app.extraction.llm import FakeLLMClient
from app.qa.soru_cevap import soru_cevapla


def _ornek_maddeler():
    return [
        ParsedArticle(number="18", title="Alt yükleniciler", body="Alt yüklenici idarenin iznine tabidir"),
        ParsedArticle(number="30", title="Geçici teminat", body="Teklif bedelinin %3 ü teminat"),
        ParsedArticle(number="7", title="Yeterlik", body="İş deneyimi istenir"),
    ]


def test_cevap_ve_kaynak_doner():
    """soru_cevapla iki şey döndürmeli: cevap (metin) + kaynaklar (madde listesi)."""
    maddeler = _ornek_maddeler()
    fake_llm = FakeLLMClient(canned_response="Test cevabı")
    fake_emb = FakeEmbeddingClient()

    cevap, kaynaklar = soru_cevapla("bir soru", maddeler, fake_emb, fake_llm, n=2)


    assert cevap == "Test cevabı"
    assert len(kaynaklar) == 2
    for k in kaynaklar:
        assert isinstance(k, ParsedArticle)


def test_prompt_baglami_iceriyor():
    """Sahte LLM'e giden prompt, bulunan maddelerin metnini içermeli
    (yani bağlam gerçekten prompt'a konmuş mu)."""
    maddeler = _ornek_maddeler()
    fake_llm = FakeLLMClient(canned_response="x")
    fake_emb = FakeEmbeddingClient()

    soru_cevapla("bir soru", maddeler, fake_emb, fake_llm, n=3)
    assert "Alt yüklenici idarenin iznine tabidir" in fake_llm.last_prompt