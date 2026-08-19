from __future__ import annotations
import hashlib, math, re
from dataclasses import dataclass
from .config import settings

@dataclass
class AIAnswer:
    text: str
    groundedness: int

class AIProvider:
    def embed(self, text: str) -> list[float]: raise NotImplementedError
    def answer(self, question: str, evidence: list[str]) -> AIAnswer: raise NotImplementedError

class LocalDeterministicProvider(AIProvider):
    def embed(self, text: str) -> list[float]:
        dims=settings.local_embedding_dimensions
        values=[0.0]*dims
        tokens=re.findall(r"[a-zA-ZÀ-ÿ0-9]+", text.lower())
        for token in tokens:
            digest=hashlib.sha256(token.encode()).digest()
            idx=int.from_bytes(digest[:2],"big")%dims
            values[idx]+=1.0 if digest[2]%2==0 else -1.0
        norm=math.sqrt(sum(v*v for v in values)) or 1.0
        return [round(v/norm,6) for v in values]

    def answer(self, question: str, evidence: list[str]) -> AIAnswer:
        if not evidence:
            return AIAnswer("Não há evidência autorizada suficiente para produzir uma resposta fundamentada.",0)
        body=" ".join(evidence[:2])
        return AIAnswer(f"Com base na base autorizada: {body}", min(98, 82 + len(evidence)*4))

def provider() -> AIProvider:
    return LocalDeterministicProvider()
