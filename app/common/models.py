"""
Ayrıştırılmış belge için veri modelleri.

Tasarım notu: Parser'ın çıktısı, ham metin değil *yapılandırılmış* bir belgedir.
Her madde kendi numarası, başlığı ve metniyle ayrı bir nesne olur. Atıf (citation)
yeteneğimiz buradan gelir: bir bilgiyi rapor ederken hangi maddeden geldiğini
ParsedArticle.number ile gösterebiliriz.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class DocumentType(str, Enum):
    """Belge türü. v1 yalnızca bu iki türü hedefler; gerisi kapsam dışı."""
    IDARI_SARTNAME = "idari_sartname"
    SOZLESME_TASARISI = "sozlesme_tasarisi"
    UNKNOWN = "unknown"


class TemplateVariant(str, Enum):
    """
    Veri analizinde iki tip şablon varyantı tespit ettik:
    - FIZIKI: pazarlık usulü, fiziki başvuru (6 bölüm, ~51 madde)
    - E_IHALE: elektronik teklif (4 bölüm, ~47 madde)
    Madde numaraları varyantlar arası kayabildiği için eşleştirmeyi
    numaraya değil başlığa göre yapacağız.
    """
    FIZIKI = "fiziki"
    E_IHALE = "e_ihale"
    UNKNOWN = "unknown"


@dataclass
class ParsedArticle:
    """Tek bir madde: 'Madde 30 - Geçici teminat ...' ve altındaki metin."""
    number: str            # "30", "7.5.1" gibi (alt bent destekli)
    title: str             # "Geçici teminat"
    body: str              # maddenin tam metni
    section: str | None = None   # ait olduğu Roma rakamlı bölüm (örn. "IV")
    page: int | None = None      # PDF'lerde sayfa; Word-HTML'de None

    def char_count(self) -> int:
        return len(self.body)


@dataclass
class ParsedDocument:
    """Bir belgenin ayrıştırılmış tam hali."""
    source_path: str
    doc_type: DocumentType
    variant: TemplateVariant
    articles: list[ParsedArticle] = field(default_factory=list)
    raw_text: str = ""
    warnings: list[str] = field(default_factory=list)   # ayrıştırma uyarıları

    def article_count(self) -> int:
        return len(self.articles)

    def find_article(self, number: str) -> ParsedArticle | None:
        """Numaraya göre madde bul (örn. '30')."""
        for a in self.articles:
            if a.number == number:
                return a
        return None

    def find_by_title_keyword(self, keyword: str) -> list[ParsedArticle]:
        """
        Başlıkta anahtar kelime geçen maddeleri bul.
        Numara varyantlar arası kaydığı için asıl güvenilir yol budur.
        Örn: find_by_title_keyword('teminat') -> geçici + kesin teminat maddeleri
        """
        kw = keyword.casefold()
        return [a for a in self.articles if kw in a.title.casefold()]


    def find_by_section(self, section: str) -> list[ParsedArticle]:

        s = section.casefold()

        return [a for a in self.articles if a.section is not None and s == a.section.casefold()]
