from dotenv import load_dotenv
load_dotenv()

from deneme import TranslatorClient

t = TranslatorClient()
sonuc = t.translate("Merhaba, bugün hava çok güzel ve ben kod yazmayı öğreniyorum.")
print("Çeviri:", sonuc)