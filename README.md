# BidAi — Kamu İhale Şartnamesi Analiz Asistanı

Kamu ihale şartnamelerini okuyup teklif verenlere yapılandırılmış özet, risk analizi ve kaynak atıflı soru-cevap sunan bir AI asistanı.

## Problem

Kamu ihale şartnameleri uzun ve karmaşıktır; firmaların teklif vermeden önce bu belgeleri dikkatlice okuyup analiz etmesi gerekir. Risk, yeterlilik ve teminat gibi kritik bilgileri elle çıkarmak ciddi bir zaman kaybıdır ve gözden kaçırma ihtimali yüksektir. Üstelik kaçırılan tek bir  madde, elenmeye veya beklenmedik maliyetlere yol açabilir. Bu asistan, o analizi otomatikleştirerek belgeden yapılandırılmış bilgi, risk değerlendirmesi ve kaynak atıflı cevaplar üretir.

## Özellikler

- **Yapılandırılmış Özet Çıkarma:** Belgeden teminat oranları, yeterlilik kriterleri, ceza maddeleri gibi bilgileri yapılandırılmış (JSON) olarak çıkarır.
- **Risk Analizi:** Şartnameyi teklif verenin gözünden risklere çevirir — elenme, maliyet, nakit ve süre riskleri; önceliklendirilmiş ve kaynak atıflı.
- **Belge Üzerine Soru-Cevap (RAG):** Belgeye serbest soru sorulabilir; sistem ilgili maddeleri bulup (retrieval) kaynak atıflı cevap üretir (generation).

## Mimari

1- Parse: Sistem öncelikle gelen belgeyi parse ederek şartnamedeki uzun maddeleri ayrıştırır.
2- Extraction: Bu maddelerin Claude API kullanılarak JSON formatında yapılandırılmış bir özeti çıkarılır. Pydantic yardımıyla verinin JSON formatına uygun olup olmadığı denetlenir.
3- Risk Analizi: Extraction çıktısından Claude API yardımıyla risk raporu oluşturulur. Bu risk raporu önem sırası ve risk derecesi belirtilerek kullanıcıya sunulur.
4- RAG: Kullanıcıdan alınan soru embed edilerek, kosinüs benzerliği yardımıyla parse edilmiş metinden seçilen ilgili maddeler ile Claude API'a gönderilir ve kullanıcıya en alakalı maddeler referans gösterilerek cevap döner.
5- API: FastAPI kullanılarak sunum katmanı oluşturulur.
6- DI: LLM/Embedding gibi dependency injectionlar arayüz arkasına alınarak sistemin test edilebilirliği sağlanıp, sadeleştirilmiştir.

Proje yapısı:

```
app/
  parsing/      # Belge ayrıştırma (.doc, .pdf → maddeler)
  extraction/   # LLM ile yapılandırılmış bilgi çıkarma (Pydantic şemaları)
  qa/           # RAG: embedding, retrieval, soru-cevap
  risk/         # Risk analizi
  api/          # FastAPI REST API (sunum katmanı)
tests/          # Birim testleri (pytest)
data/samples/   # Örnek şartnameler
```

## Kurulum

**Gereksinimler:** Python 3.9+

```bash
# 1. Sanal ortam oluştur ve etkinleştir
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Bağımlılıkları kur
pip install -r requirements.txt

# 3. API anahtarını ayarla (.env dosyası oluştur)
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

## Çalıştırma

```bash
# API sunucusunu başlat
uvicorn app.api.main:app --reload

# Tarayıcıda aç:
#   http://127.0.0.1:8000/docs    -> interaktif API dokümantasyonu (Swagger)
#   http://127.0.0.1:8000/health  -> sağlık kontrolü
```

## API Uç Noktaları

| Metod | Yol       | Açıklama                                        |
|-------|-----------|-------------------------------------------------|
| GET   | `/health` | Sağlık kontrolü                                 |
| POST  | `/ozet`   | Belge metni → yapılandırılmış özet              |
| POST  | `/risk`   | Belge metni → risk raporu                       |
| POST  | `/soru`   | Belge dosyası + soru → kaynak atıflı cevap (RAG)|

## Testler

```bash
pytest -v
```

## Kapsam ve Sınırlar

**Destekleniyor:**
- Yapım işi idari şartnameleri ve sözleşme tasarıları
- Word-HTML ve metin-tabanlı (text-layer içeren) PDF belgeleri

**Henüz desteklenmiyor:**
- Teknik şartnameler (sektöre göre yapıları çok değişken; bilinçli olarak v2'ye bırakıldı)
- Taranmış / görüntü-tabanlı PDF'ler (OCR gerektirir)
- Modern .docx formatı (parser şu an Word-HTML bekliyor)

**Bilinen sınırlar:**
- Retrieval mükemmel değil; bazı sorularda ilgili madde ilk sonuçlara giremeyebilir (başlık+gövde embed ile iyileştirildi, daha da geliştirilebilir).
- Vektörler bellekte tutuluyor; production için kalıcı bir vektör deposu (ör. pgvector) gerekir.
- 
## Teknolojiler

Python · FastAPI · Anthropic Claude · Pydantic · sentence-transformers · pytest