from app.extraction.llm import FakeLLMClient
from app.extraction.ozet_extractor import extract_ozet


def test_extract_ozet():
    sahte_json = '{"ihale_konusu": "Test işi", "gecici_teminat_orani": "%3"}'
    sahte_llm = FakeLLMClient(canned_response=sahte_json)
    ozet = extract_ozet("herhangi bir belge metni", sahte_llm)

    assert ozet.ihale_konusu == "Test işi"
    assert ozet.gecici_teminat_orani == "%3"