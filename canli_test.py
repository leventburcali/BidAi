from dotenv import load_dotenv
load_dotenv()

from app.parsing.parser import parse_document
from app.extraction.claude_client import ClaudeLLMClient
from app.extraction.extractor import extract_teminat_orani

# Gerçek belgeden teminat maddesini al
doc = parse_document("data/samples/2020-108658_idari_sartname.doc")
madde = doc.find_by_title_keyword("geçici teminat")[0]
print("Madde:", madde.number, "-", madde.title)

# GERÇEK Claude ile extraction
claude = ClaudeLLMClient()
sonuc = extract_teminat_orani(madde.body, claude)
print("Claude'un çıkardığı teminat oranı:", sonuc)