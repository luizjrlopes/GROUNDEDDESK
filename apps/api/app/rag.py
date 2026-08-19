from __future__ import annotations
import re
from sqlalchemy import select
from sqlalchemy.orm import Session
from .ai import provider
from .domain import reciprocal_rank_fusion
from .models import KnowledgeChunk, KnowledgeDocument

def _lexical_score(query: str, text: str) -> float:
    q=set(re.findall(r"[a-zA-ZÀ-ÿ0-9]+",query.lower()))
    t=set(re.findall(r"[a-zA-ZÀ-ÿ0-9]+",text.lower()))
    return len(q&t)/(len(q) or 1)

def search(db: Session, *, org_id: str, query: str, scope: str | None=None, hybrid: bool=True, limit: int=6) -> list[dict]:
    stmt=select(KnowledgeChunk, KnowledgeDocument).join(KnowledgeDocument, KnowledgeDocument.id==KnowledgeChunk.document_id).where(KnowledgeChunk.org_id==org_id, KnowledgeDocument.status=="Indexado")
    if scope: stmt=stmt.where(KnowledgeDocument.scope==scope)
    rows=db.execute(stmt).all()
    qvec=provider().embed(query)
    scored=[]
    for chunk,doc in rows:
        lexical=_lexical_score(query,chunk.content)
        emb=list(chunk.embedding or [])
        dot=sum(a*b for a,b in zip(qvec,emb)) if emb else 0.0
        scored.append({"chunk":chunk,"doc":doc,"lexical":lexical,"vector":dot})
    lex_sorted=sorted(scored,key=lambda x:x["lexical"],reverse=True)
    vec_sorted=sorted(scored,key=lambda x:x["vector"],reverse=True)
    lex_rank={x["chunk"].id:i+1 for i,x in enumerate(lex_sorted)}
    vec_rank={x["chunk"].id:i+1 for i,x in enumerate(vec_sorted)}
    for x in scored:
        x["rerank"]=reciprocal_rank_fusion(lex_rank.get(x["chunk"].id),vec_rank.get(x["chunk"].id) if hybrid else None)
    scored.sort(key=lambda x:x["rerank"],reverse=True)
    return [{"chunk_id":x["chunk"].id,"document_id":x["doc"].id,"title":x["doc"].title,"version":x["doc"].version,"section":x["chunk"].section,"content":x["chunk"].content,"lexical":round(x["lexical"],4),"vector":round(x["vector"],4),"rerank":round(x["rerank"],6)} for x in scored[:limit]]
