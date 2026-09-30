

"""
Eval: extraction çıktısını golden set'e karşı ölçer.

Her belge için: sistemi çalıştır, çıktıyı beklenen (golden) değerlerle
karşılaştır, doğru/yanlış say, sonunda genel skoru yazdır.

Esnek eşleşme: sistemin cevabı golden değerini İÇERİYORSA doğru sayılır
(böylece "%6, sınır değer altında %9" gibi daha zengin cevaplar da doğru).
"""
from dotenv import load_dotenv
load_dotenv()

from app.parsing.parser import parse_document
from app.extraction.claude_client import ClaudeLLMClient
from app.extraction.ozet_extractor import extract_ozet
from eval.golden import GOLDEN_SET


def _normalize(metin: str) -> str:
    """Karşılaştırma için metni sadeleştir: boşlukları kaldır, küçük harf."""
    if metin is None:
        return ""
    return metin.replace(" ", "").lower()

def _dogru_mu(beklenen, gercek):
    if beklenen is None:
        return gercek is None      # negatif: ikisi de None mı?
    if gercek is None:
        return False               # bir şey bekliyorduk, None geldi
    return _normalize(beklenen) in _normalize(gercek)


def calistir():
    claude = ClaudeLLMClient()
    toplam = 0
    dogru = 0

    for ornek in GOLDEN_SET:
        yol = ornek["dosya"]
        beklenen = ornek["beklenen"]

        doc = parse_document(yol)
        ozet = extract_ozet(doc.raw_text, claude)

        print(f"\n=== {yol} ===")
        for alan, beklenen_deger in beklenen.items():
            if "." in alan:
                ust, alt = alan.split(".")  # "idare_bilgisi.ikn" -> "idare_bilgisi", "ikn"
                ust_nesne = getattr(ozet, ust)  # ozet.idare_bilgisi
                gercek_deger = getattr(ust_nesne, alt) if ust_nesne else None  # .ikn (idare None ise None)
            else:
                gercek_deger = getattr(ozet, alan)  # düz alan (eskisi gibi)
            sonuc = _dogru_mu(beklenen_deger, gercek_deger)
            toplam += 1
            if sonuc:
                dogru += 1
            isaret = "✓" if sonuc else "✗"
            print(f"  {isaret} {alan}: beklenen={beklenen_deger!r}, gercek={gercek_deger!r}")

    print(f"\n{'='*40}")
    print(f"SONUÇ: {dogru}/{toplam} doğru  (%{100*dogru//toplam if toplam else 0})")


if __name__ == "__main__":
    calistir()