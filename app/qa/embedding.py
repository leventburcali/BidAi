from typing import Protocol


class EmbeddingClient(Protocol):
    def embed(self, text:str) -> list[float]:
        ...

class LocalEmbeddingClient:
    def __init__(self, model_adi: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_adi)

    def embed(self, text:str) -> list[float]:
        vektor = self.model.encode(text).tolist()
        return vektor

class FakeEmbeddingClient:
    """Test için sahte embedding. Gerçek model yüklemez.
    Deterministik: aynı metin -> aynı vektör, farklı metin -> farklı vektör."""

    def __init__(self, boyut: int = 8):
        self.boyut = boyut       # sahte vektörün uzunluğu (küçük tutuyoruz)

    def embed(self, text: str) -> list[float]:
        toplam = sum(ord(c) for c in text)
        vektor = []
        for i in range(self.boyut):
            deger = float((toplam+i)%100)
            vektor.append(deger)
        return vektor