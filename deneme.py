import os



class TranslatorClient:
    def __init__(self, model: str = "claude-haiku-4-5"):
        from anthropic import Anthropic
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY bulunamadı. Anahtarı .env dosyasına ekleyin.")

        self.client = Anthropic(api_key = api_key)
        self.model = model


    def translate(self, text: str) -> str:
       prompt = f"Aşağıdaki metni İngilizceye çevir. Sadece çeviriyi ver, açıklama ekleme:\n\n{text}"
       response = self.client.messages.create(model=self.model,
                                    max_tokens=1024,
                                    messages=[{"role": "user", "content": prompt}],)
       return response.content[0].text

