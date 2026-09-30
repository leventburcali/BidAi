from dotenv import load_dotenv
load_dotenv()

from app.parsing.parser import parse_document
from app.extraction.claude_client import ClaudeLLMClient
from app.extraction.ozet_extractor import extract_ozet
from app.risk.analiz import risk_analiz_et

doc = parse_document("data/samples/2020-108658_idari_sartname.doc")
claude = ClaudeLLMClient()

# ZİNCİR: belge → özet → riskler
print("1. Özet çıkarılıyor...")
ozet = extract_ozet(doc.raw_text, claude)

print("2. Risk analizi yapılıyor...")
rapor = risk_analiz_et(ozet, claude)

print("\n=== RİSK RAPORU ===")
if rapor.genel_degerlendirme:
    print("Genel:", rapor.genel_degerlendirme)
print()
for r in rapor.riskler:
    print(f"[{r.onem}] {r.kategori}: {r.aciklama}")
    print(f"   Kaynak: {r.kaynak}\n")