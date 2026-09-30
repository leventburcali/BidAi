"""
Hızlı deneme scripti: tüm örnek belgeleri ayrıştırıp özet basar.
Çalıştırma:  python run_parser_demo.py
"""
import glob
from app.parsing.parser import parse_document

print("=== İdari şartnameler ===")
for f in sorted(glob.glob("data/samples/*_idari_sartname.doc")):
    doc = parse_document(f)
    tem = doc.find_by_title_keyword("teminat")
    ilk = tem[0] if tem else None
    print(f"{f.split('/')[-1]:42s} {doc.doc_type.value:16s} {doc.variant.value:8s} "
          f"madde={doc.article_count():3d}  geçici teminat → Madde {ilk.number if ilk else '?'}")

print("\n=== Sözleşme tasarıları ===")
for f in sorted(glob.glob("data/samples/*_sozlesme_tasarisi.doc")):
    doc = parse_document(f)
    ceza = doc.find_by_title_keyword("ceza")
    print(f"{f.split('/')[-1]:42s} {doc.doc_type.value:18s} "
          f"madde={doc.article_count():3d}  ceza maddeleri: {[a.number for a in ceza]}")

print("\n=== Bölüm testi ===")
doc = parse_document("data/samples/2020-108658_idari_sartname.doc")

bolumler = sorted(set(a.section for a in doc.articles if a.section is not None))
print("Belgedeki bölümler:", bolumler)

for b in bolumler:
    maddeler = doc.find_by_section(b)
    numaralar = [a.number for a in maddeler]
    print(f"Bölüm {b}: {len(maddeler)} madde -> {numaralar}")

