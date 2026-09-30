# 1. Temel imaj: Python 3.9 kurulu hafif bir başlangıç kutusu
#    "slim" = gereksiz araçlar olmadan, daha küçük
FROM python:3.9-slim

# 2. Konteyner içinde çalışma dizini (kodun yaşayacağı yer)
WORKDIR /app

# 3. Önce SADECE requirements.txt'i kopyala ve bağımlılıkları kur
#    (Neden önce sadece bu? Docker katman önbelleği için — aşağıda açıklama)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Sonra tüm proje kodunu kopyala
COPY . .

# 5. API'nin çalışacağı portu belirt (bilgi amaçlı)
EXPOSE 8000

# 6. Konteyner başlayınca çalışacak komut
#    host 0.0.0.0 = konteyner dışından erişilebilir olsun (127.0.0.1 sadece içeriden)
CMD uvicorn app.api.main:app --host 0.0.0.0 --port ${PORT:-8080}