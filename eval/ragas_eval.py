from app.extraction.claude_client import ClaudeLLMClient
from app.parsing.parser import parse_document
from app.qa.chroma_store import sorgula, indexle

from dotenv import load_dotenv

from app.qa.embedding import LocalEmbeddingClient

load_dotenv()

from ragas import evaluate, EvaluationDataset
from ragas.metrics import Faithfulness
from ragas.llms import LangchainLLMWrapper
from langchain_anthropic import ChatAnthropic
from ragas.metrics import Faithfulness, LLMContextPrecisionWithReference, LLMContextRecall




def eval_seti_olustur(sorular_referanslar, col, embedding, llm) -> list[dict]:

    ornekler = []

    for soru, referans in sorular_referanslar:
        contexts = sorgula(col, soru, embedding)
        context_text = "\n\n".join(contexts)
        prompt = f"Aşağıdaki maddelere dayanarak cevapla:\n\n{context_text}\n\nSoru: {soru}"
        response = llm.complete(prompt)
        ornekler.append({"user_input": soru, "response": response, "retrieved_contexts": contexts, "reference": referans})

    return ornekler

if __name__ == "__main__":
    # 1. Belge → Chroma koleksiyonu
    doc = parse_document("data/samples/2020-108658_idari_sartname.doc")
    embedding = LocalEmbeddingClient()
    llm = ClaudeLLMClient()
    col = indexle(doc.articles, embedding)

    # 2. Sadece soru + referans (elle yazdığın tek şey)
    sorular_referanslar = [
        ("Geçici teminat oranı nedir?", "Geçici teminat, teklif bedelinin %3'ünden az olamaz."),
        ("Kesin teminat oranı nedir?", "İhale bedelinin %6'sı"),
    ]

    # 3. response + contexts OTOMATİK üretilir
    ornekler = eval_seti_olustur(sorular_referanslar, col, embedding, llm)

    # 4. RAGAS (mevcut evaluate kodun)
    dataset = EvaluationDataset.from_list(ornekler)
    evaluator_llm = LangchainLLMWrapper(ChatAnthropic(model="claude-haiku-4-5", temperature=0))
    sonuc = evaluate(dataset=dataset, metrics=[Faithfulness(), LLMContextPrecisionWithReference(), LLMContextRecall()], llm=evaluator_llm)
    print(sonuc)
