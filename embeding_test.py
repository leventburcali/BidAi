from app.common.models import ParsedArticle

from app.qa.embedding import LocalEmbeddingClient
from app.qa.retrieval import en_yakin_maddeler

maddeler = [
    ParsedArticle(number="7",  title="Yeterlik", body="İş deneyimi ve banka referansı istenir"),
    ParsedArticle(number="30", title="Geçici teminat", body="Teklif bedelinin yüzde üçü teminat"),
    ParsedArticle(number="42", title="Alt yüklenici", body="Alt yüklenici çalıştırmak idarenin iznine tabidir"),
]

sonuc = en_yakin_maddeler(maddeler, "taşeron kullanabilir miyim", LocalEmbeddingClient(), n=2)
print("\nGerçek embedding ile:")
for m in sonuc:
    print(f"  Madde {m.number} - {m.title}")