import chromadb

from app.common.models import ParsedArticle
from app.qa.embedding import EmbeddingClient


def indexle(maddeler: list[ParsedArticle], embedding:EmbeddingClient):
    client = chromadb.PersistentClient(path="./chroma_db")  # kalıcı client
    col = client.get_or_create_collection("maddeler")
    ids=[]
    embeddings = []
    documents=[]
    index = 0
    for i in maddeler:
        index +=1
        ids.append(str(index))
        metin = f"{i.title}\n{i.body}"
        embeddings.append(embedding.embed(metin))
        documents.append(metin)

    col.add(ids=ids, embeddings=embeddings , documents=documents)

    return col

def sorgula(col, soru:str, embedding: EmbeddingClient, n:int=5) -> list[str]:


    soru_vektoru = embedding.embed(soru)
    sonuc = col.query(query_embeddings=[soru_vektoru], n_results = n)

    return sonuc["documents"][0]

if __name__ == "__main__":
    from app.parsing.parser import parse_document
    from app.qa.embedding import LocalEmbeddingClient

    emb = LocalEmbeddingClient()
    doc = parse_document("data/samples/2020-108658_idari_sartname.doc")
    col = indexle(doc.articles, emb)
    sonuclar = sorgula(col, "geçici teminat oranı nedir?", emb)
    for s in sonuclar:
        print("---")
        print(s)