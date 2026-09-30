from dotenv import load_dotenv
load_dotenv()

from app.parsing.parser import parse_document
from app.qa.embedding import LocalEmbeddingClient
from app.extraction.claude_client import ClaudeLLMClient
from app.qa.soru_cevap import soru_cevapla

# Belgeyi ayrıştır
doc = parse_document("data/samples/2020-108658_idari_sartname.doc")

# İstemcileri kur (gerçek embedding + gerçek Claude)
embedding = LocalEmbeddingClient()
claude = ClaudeLLMClient()

# Soru sor
soru = "Alt yüklenici kullanabilir miyim?"
cevap,kaynaklar = soru_cevapla(soru, doc.articles, embedding, claude)

print("Soru:", soru)
print("Cevap:", cevap)
print("\nKaynaklar (bu cevap şu maddelere dayanıyor):")
for m in kaynaklar:
    print(f"  - Madde {m.number}: {m.title}")