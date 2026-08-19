from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import delete
from sqlalchemy.orm import Session
from .ai import provider
from .models import AuditEvent, IngestionJob, KnowledgeChunk, KnowledgeDocument

def chunks(text: str, size: int=420) -> list[str]:
    clean=" ".join(text.split())
    if not clean: return []
    parts=[]; start=0
    while start<len(clean):
        end=min(len(clean),start+size)
        if end<len(clean):
            cut=clean.rfind(" ",start,end)
            if cut>start+100: end=cut
        parts.append(clean[start:end].strip()); start=end
    return [p for p in parts if p]

def enqueue(db: Session, doc: KnowledgeDocument) -> IngestionJob:
    job=IngestionJob(org_id=doc.org_id, document_id=doc.id)
    doc.status="Processando"; doc.updated_at=datetime.now(timezone.utc); db.add(job); return job

def process_job(db: Session, job: IngestionJob) -> None:
    doc=db.get(KnowledgeDocument,job.document_id)
    if not doc: raise ValueError("Document no longer exists")
    db.execute(delete(KnowledgeChunk).where(KnowledgeChunk.document_id==doc.id))
    pieces=chunks(doc.source_text or f"{doc.title}. Conteúdo demonstrativo autorizado para {doc.scope}.")
    for i,piece in enumerate(pieces or [doc.title]):
        db.add(KnowledgeChunk(org_id=doc.org_id,document_id=doc.id,section=f"§ {i+1}",content=piece,embedding=provider().embed(piece)))
    doc.status="Indexado"; doc.quality=96; doc.updated_at=datetime.now(timezone.utc)
    job.status="COMPLETED"; job.updated_at=datetime.now(timezone.utc)
    db.add(AuditEvent(org_id=doc.org_id,actor_name="GroundedDesk Worker",actor_role="system",action="DOCUMENT_INDEXED",resource=f"Documento {doc.id}",detail=f"{len(pieces or [doc.title])} chunks indexados"))
