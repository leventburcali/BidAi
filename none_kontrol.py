from dotenv import load_dotenv
load_dotenv()

from app.parsing.parser import parse_document
from app.extraction.claude_client import ClaudeLLMClient
from app.extraction.ozet_extractor import extract_ozet

belgeler = [
    "data/samples/2020-108658_idari_sartname.doc",
    "data/samples/2020-425249_idari_sartname.doc",
    "data/samples/2020-629371_idari_sartname.doc",
    "data/samples/2020-666704_idari_sartname.doc",
]

claude = ClaudeLLMClient()

for yol in belgeler:
    doc = parse_document(yol)
    ozet = extract_ozet(doc.raw_text, claude)
    print(f"\n=== {yol} ===")
    print(f"  ihale_konusu:            {ozet.ihale_konusu!r}")
    print(f"  ihale_usulu:             {ozet.ihale_usulu!r}")
    print(f"  son_teklif_tarihi:       {ozet.son_teklif_tarihi!r}")
    print(f"  gecici_teminat_orani:    {ozet.gecici_teminat_orani!r}")
    print(f"  kesin_teminat_orani:     {ozet.kesin_teminat_orani!r}")
    print(f"  teklif_gecerlilik_suresi:{ozet.teklif_gecerlilik_suresi!r}")
    print(f"  idare_bilgisi:           {ozet.idare_bilgisi!r}")