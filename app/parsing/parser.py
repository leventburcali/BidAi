
from __future__ import annotations

import re
from pathlib import Path

from bs4 import BeautifulSoup

from app.common.models import (
    DocumentType,
    ParsedArticle,
    ParsedDocument,
    TemplateVariant,
)

ARTICLE_RE = re.compile(r"^\s*Madde\s+(\d+(?:\.\d+)*)\s*[-–]\s*(.*)$", re.IGNORECASE)
SECTION_RE = re.compile(r"^\s*([IVXLC]+)\s*[-–]\s*(.+)$")


def _decode_word_html(raw: bytes) -> str:
    """
    Word-HTML baytlarını doğru kodlamayla metne çevirir.
    Strateji: önce HTML içindeki charset meta etiketini ara; bulunamazsa
    EKAP belgelerinde standart olan ISO-8859-9'a (Latin-5 / Türkçe) düş.
    """
    head = raw[:2048].decode("ascii", errors="ignore").lower()
    m = re.search(r'charset=([\w-]+)', head)
    encoding = m.group(1) if m else "iso-8859-9"
    try:
        return raw.decode(encoding, errors="replace")
    except LookupError:
        return raw.decode("iso-8859-9", errors="replace")


def _html_to_lines(html: str) -> list[str]:
    """HTML'i temiz, boş olmayan satır listesine çevirir."""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n")
    return [ln.strip() for ln in text.split("\n") if ln.strip()]


def _looks_like_word_html(raw: bytes) -> bool:
    """'.doc' aslında HTML mi, yoksa gerçek ikili Word mü?"""
    head = raw[:1024].lower()
    return b"<html" in head or b"mso" in head or b"<!doctype html" in head


# --- Belge türü ve varyant tespiti --------------------------------------------
def _tr_lower(s: str) -> str:
    """Türkçe-güvenli küçük harf: İ/I ve ş gibi karakterleri normalize eder."""
    return s.replace("İ", "i").replace("I", "ı").lower()


def detect_doc_type(lines: list[str]) -> DocumentType:
    head = _tr_lower(" ".join(lines[:15]))
    if "sözleşme" in head and "tasarı" in head:
        return DocumentType.SOZLESME_TASARISI
    if "şartname" in head:
        # idari mi teknik mi? teknik şartname v1 kapsamı dışında
        if "idari" in head:
            return DocumentType.IDARI_SARTNAME
        return DocumentType.UNKNOWN
    return DocumentType.UNKNOWN


def detect_variant(lines: list[str]) -> TemplateVariant:

    full = " ".join(lines).casefold()
    if "yeterlik bilgileri tablosu" in full or "e-teklif" in full or "elektronik ortamda" in full:
        return TemplateVariant.E_IHALE
    return TemplateVariant.FIZIKI


# --- Maddelere bölme ----------------------------------------------------------
def _split_into_articles(lines: list[str]) -> tuple[list[ParsedArticle], list[str]]:
    """
    Satır listesini maddelere böler. Bir 'Madde N - Başlık' satırı görülünce
    yeni madde başlar; sonraki satırlar bir sonraki maddeye kadar onun gövdesi olur.
    Roma rakamlı bölüm başlıkları takip edilip her maddeye section olarak işlenir.
    """
    articles: list[ParsedArticle] = []
    warnings: list[str] = []
    current_section: str | None = None
    cur: ParsedArticle | None = None
    body_lines: list[str] = []

    def _flush():
        nonlocal cur, body_lines
        if cur is not None:
            cur.body = "\n".join(body_lines).strip()
            articles.append(cur)
        cur, body_lines = None, []

    for ln in lines:
        sec = SECTION_RE.match(ln)
        art = ARTICLE_RE.match(ln)
        if art:
            _flush()
            cur = ParsedArticle(
                number=art.group(1),
                title=art.group(2).strip(),
                body="",
                section=current_section,
            )
        elif sec and sec.group(2).isupper():
            # Bölüm başlığı yalnızca madde dışındayken geçerli sayılır
            current_section = sec.group(1)
        else:
            if cur is not None:
                body_lines.append(ln)
    _flush()

    if not articles:
        warnings.append("Hiç 'Madde N -' deseni bulunamadı; belge yapısı beklenenden farklı.")
    return articles, warnings


# --- PDF hattı ----------------------------------------------------------------
def _parse_pdf(path: Path) -> ParsedDocument:
    """
    PDF'i ayrıştırır. Taranmışsa erken çıkıp uyarı döndürür (madde bölme yapmaz).
    Metin tabanlıysa, her satıra geldiği sayfayı işleyerek Word-HTML hattıyla
    aynı madde-bölme mantığını uygular.
    """
    from app.parsing.pdf_loader import load_pdf

    result = load_pdf(path)

    if result.is_probably_scanned:
        return ParsedDocument(
            source_path=str(path),
            doc_type=DocumentType.UNKNOWN,
            variant=TemplateVariant.UNKNOWN,
            raw_text=result.full_text,
            warnings=[
                "Belge taranmış (görüntü) görünüyor: sayfa başına çok az metin "
                f"çıktı ({result.total_chars} karakter / {len(result.pages)} sayfa). "
                "v1 yalnızca metin tabanlı PDF'leri destekler."
            ],
        )

    # Sayfa bilgisini koruyarak satırlara ayır
    lines: list[str] = []
    line_pages: list[int] = []
    for page in result.pages:
        for ln in page.text.split("\n"):
            s = ln.strip()
            if s:
                lines.append(s)
                line_pages.append(page.number)

    doc_type = detect_doc_type(lines)
    variant = detect_variant(lines)
    articles, warnings = _split_into_articles(lines)

    return ParsedDocument(
        source_path=str(path),
        doc_type=doc_type,
        variant=variant,
        articles=articles,
        raw_text="\n".join(lines),
        warnings=warnings,
    )


# --- Genel yükleyici ----------------------------------------------------------
def parse_document(path: str | Path) -> ParsedDocument:

    path = Path(path)
    raw = path.read_bytes()
    warnings: list[str] = []

    if path.suffix.lower() == ".pdf":
        return _parse_pdf(path)

    # Word-HTML hattı
    if not _looks_like_word_html(raw):
        warnings.append("'.doc' dosyası HTML görünmüyor; ikili Word olabilir, sonuç şüpheli.")
    html = _decode_word_html(raw)
    lines = _html_to_lines(html)

    doc_type = detect_doc_type(lines)
    variant = detect_variant(lines)
    articles, w = _split_into_articles(lines)
    warnings.extend(w)

    return ParsedDocument(
        source_path=str(path),
        doc_type=doc_type,
        variant=variant,
        articles=articles,
        raw_text="\n".join(lines),
        warnings=warnings,
    )
