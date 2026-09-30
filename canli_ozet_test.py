from dotenv import load_dotenv
load_dotenv()

from app.parsing.parser import parse_document
from app.extraction.claude_client import ClaudeLLMClient
from app.extraction.ozet_extractor import extract_ozet

# 1. Belgeyi ayrıştır
doc = parse_document("data/samples/2020-108658_idari_sartname.doc")

# 2. Claude istemcisi oluştur
claude = ClaudeLLMClient()

# 3. Özeti çıkar (belgenin TÜM metnini ver)
ozet = extract_ozet(doc.raw_text, claude)

# 4. Alanları yazdır
print("İhale konusu:", ozet.ihale_konusu)
print("İhale usulü:", ozet.ihale_usulu)

print("Geçici teminat:", ozet.gecici_teminat_orani)
print("Kesin teminat:", ozet.kesin_teminat_orani)

# Belgede gerçekte ne yazıyor, kontrol edelim
for m in doc.find_by_title_keyword("teminat"):
    print(f"\nMadde {m.number} - {m.title}")
    print(m.body[:200])

print("\nYeterlilik kriterleri:")
for k in ozet.yeterlilik_kriterleri:
    print(f"  - {k.tur}: {k.aciklama} (oran: {k.oran})")

print("\nİdare bilgisi:")
if ozet.idare_bilgisi:
    print("  Adı:", ozet.idare_bilgisi.adi)
    print("  İKN:", ozet.idare_bilgisi.ikn)
else:
    print("  (bulunamadı)")

print("\nCeza maddeleri:")
for c in ozet.ceza_maddeleri:
    print(f"  - {c.tur}: {c.oran} ({c.aciklama})")