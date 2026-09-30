"""
PDF yükleme hattı (pdfplumber).

Sorumluluğu dar: bir PDF'ten sayfa sayfa metin çıkarır ve belgenin
'taranmış mı' olduğunu kestirir. Madde bölme / tür tespiti parser.py'de yapılır;
bu modül yalnızca ham metni ve sayfa bilgisini üretir.

Taranmış tespiti neden önemli? v1 yalnızca metin tabanlı PDF'leri destekler.
Taranmış (görüntü) PDF'lerde gömülü metin ya hiç yoktur ya çok azdır; bunları
OCR'sız işleyemeyiz, o yüzden erkenden tespit edip reddederiz (T07).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class PdfPage:
    number: int          # 1'den başlayan sayfa numarası
    text: str


@dataclass
class PdfLoadResult:
    pages: list[PdfPage]
    is_probably_scanned: bool
    total_chars: int

    @property
    def full_text(self) -> str:
        return "\n".join(p.text for p in self.pages)


# Taranmış kabul etme eşiği: sayfa başına ortalama bu kadar karakterden
# az metin çıkıyorsa, belge büyük olasılıkla görüntü (taranmış) içeriyordur.
MIN_CHARS_PER_PAGE = 80


def load_pdf(path: str | Path) -> PdfLoadResult:
    """PDF'i sayfa sayfa okur. pdfplumber içe aktarımı fonksiyon içinde tutulur
    ki modül, pdfplumber kurulu olmadan da en azından import edilebilsin."""
    import pdfplumber

    path = Path(path)
    pages: list[PdfPage] = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages.append(PdfPage(number=i, text=text))

    total_chars = sum(len(p.text) for p in pages)
    avg = total_chars / len(pages) if pages else 0
    is_scanned = avg < MIN_CHARS_PER_PAGE

    return PdfLoadResult(
        pages=pages,
        is_probably_scanned=is_scanned,
        total_chars=total_chars,
    )
