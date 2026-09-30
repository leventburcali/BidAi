from app.extraction.llm import FakeLLMClient
from app.extraction.extractor import extract_teminat_orani


def test_extract_teminat_orani():
    sahte_llm = FakeLLMClient(canned_response="%3")
    sonuc = extract_teminat_orani("teklif bedelinin %3'ü kadar teminat", sahte_llm)
    assert sonuc == "%3"


def test_prompt_madde_metnini_icerir():
    sahte_llm = FakeLLMClient(canned_response="%3")
    extract_teminat_orani("BENZERSIZ_TEST_METNI_12345", sahte_llm)
    assert "BENZERSIZ_TEST_METNI_12345" in sahte_llm.last_prompt
