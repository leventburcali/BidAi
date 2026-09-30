"""
Retrieval testleri — sahte embedding ile fonksiyonun MEKANİĞİNİ doğrular.
(Anlamsal doğruluk gerçek embedding'in işi; burada 'kaç madde döndü,
doğru tip mi, kenar durumlar' gibi mekanik garantiler test edilir.)
"""
from app.common.models import ParsedArticle
from app.qa.embedding import FakeEmbeddingClient
from app.qa.retrieval import en_yakin_maddeler


def _ornek_maddeler():
    return [
        ParsedArticle(number="1", title="A", body="birinci madde metni"),
        ParsedArticle(number="2", title="B", body="ikinci madde metni"),
        ParsedArticle(number="3", title="C", body="üçüncü madde metni"),
        ParsedArticle(number="4", title="D", body="dördüncü madde metni"),
    ]


def test_dogru_sayida_madde_doner():
    """n kaç ise o kadar madde dönmeli."""
    maddeler = _ornek_maddeler()
    sonuc = en_yakin_maddeler(maddeler, "bir soru", FakeEmbeddingClient(), n=2)
    assert len(sonuc) == 2


def test_donen_seyler_madde():
    """Dönen her eleman bir ParsedArticle olmalı."""
    maddeler = _ornek_maddeler()
    sonuc = en_yakin_maddeler(maddeler, "bir soru", FakeEmbeddingClient(), n=3)
    for m in sonuc:
        assert isinstance(m, ParsedArticle)


def test_n_madde_sayisindan_buyukse():
    """n, madde sayısından büyükse, var olan tüm maddeler dönmeli (çökmeden)."""
    maddeler = _ornek_maddeler()   # 4 madde
    sonuc = en_yakin_maddeler(maddeler, "bir soru", FakeEmbeddingClient(), n=10)
    assert len(sonuc) == 4
    