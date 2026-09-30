
from __future__ import annotations

import numpy as np

from app.common.models import ParsedArticle
from app.qa.embedding import EmbeddingClient


def _kosinus_benzerligi(a: list[float], b: list[float]) -> float:
    """İki vektör arasındaki kosinüs benzerliği (1.0 = aynı yön, 0 = alakasız)."""
    va, vb = np.array(a), np.array(b)
    return float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb)))


def en_yakin_maddeler(
    maddeler: list[ParsedArticle],
    soru: str,
    embedding: EmbeddingClient,
    n: int = 5,
) -> list[ParsedArticle]:

    # 1. Soruyu embed et
    soru_vektoru = embedding.embed(soru)

    # 2. Her madde için benzerlik hesapla, (madde, skor) çiftlerini topla
    skorlu = []
    for madde in maddeler:
        metin = f"{madde.title}\n{madde.body}"
        madde_vektoru = embedding.embed(metin)
        skor = _kosinus_benzerligi(soru_vektoru, madde_vektoru)
        skorlu.append((madde, skor))

    skorlu.sort(key=lambda x: x[1], reverse=True)

    return [cift[0] for cift in skorlu[:n]]