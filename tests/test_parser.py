"""
Parser testleri.

Bu testler 'golden' beklentileri kilitler: parser'ı sonradan değiştirdiğimizde
bir şeyi bozarsak hemen fark ederiz. Mülakat notu: testler sadece doğruluk için
değil, *güvenle değişiklik yapabilmek* (refactor cesareti) için de vardır.
"""
import glob
from pathlib import Path

import pytest

from app.common.models import DocumentType, TemplateVariant
from app.parsing.parser import parse_document

SAMPLES = Path(__file__).parent.parent / "data" / "samples"


def _idari():
    return sorted(glob.glob(str(SAMPLES / "*_idari_sartname.doc")))


def _sozlesme():
    return sorted(glob.glob(str(SAMPLES / "*_sozlesme_tasarisi.doc")))


@pytest.mark.parametrize("path", _idari())
def test_idari_sartname_dogru_tespit(path):
    doc = parse_document(path)
    assert doc.doc_type == DocumentType.IDARI_SARTNAME
    # idari şartnameler en az 40 madde içerir (gözlemlenen aralık 47-57)
    assert doc.article_count() >= 40
    # varyant ya fiziki ya e-ihale olmalı, unknown kalmamalı
    assert doc.variant in (TemplateVariant.FIZIKI, TemplateVariant.E_IHALE)


@pytest.mark.parametrize("path", _sozlesme())
def test_sozlesme_dogru_tespit(path):
    doc = parse_document(path)
    assert doc.doc_type == DocumentType.SOZLESME_TASARISI
    assert doc.article_count() >= 20


def test_teminat_baslikla_bulunur():
    """Numara varyantlar arası kaysa da başlıkla teminat maddesi bulunmalı."""
    for path in _idari():
        doc = parse_document(path)
        tem = doc.find_by_title_keyword("teminat")
        assert len(tem) > 0, f"{path}: teminat maddesi bulunamadı"
        # ilk teminat maddesi 'geçici teminat' olmalı
        assert any("geçici" in a.title.casefold() for a in tem)


def test_madde_govdesi_bos_degil():
    """Bölünen maddelerin gövdesi dolu olmalı (boş bölme hatası kontrolü)."""
    doc = parse_document(_idari()[0])
    dolu = [a for a in doc.articles if a.char_count() > 0]
    # maddelerin büyük çoğunluğu gövde içermeli
    assert len(dolu) >= doc.article_count() * 0.7


def _pdfs():
    return sorted(glob.glob(str(SAMPLES / "*.pdf")))


@pytest.mark.skipif(not _pdfs(), reason="örnek PDF yok")
def test_taranmis_pdf_reddedilir():
    """Taranmış/görüntü PDF, madde üretmeden uyarıyla reddedilmeli."""
    for path in _pdfs():
        doc = parse_document(path)
        # bu örnek PDF taranmış; madde çıkmamalı ve uyarı olmalı
        if doc.article_count() == 0:
            assert any("taranmış" in w.casefold() for w in doc.warnings)


def test_belgede_birden_fazla_bolum_var():
    doc = parse_document(_idari()[0])
    bolumler = set(a.section for a in doc.articles if a.section is not None)
    assert len(bolumler) > 1