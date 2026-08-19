from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from ..audit import record
from ..db import get_db
from ..ingestion import enqueue
from ..models import KnowledgeChunk, KnowledgeDocument, User, uid
from ..schemas import DocumentCreate, DocumentUpdate
from ..security import require
router=APIRouter(prefix="/knowledge",tags=["knowledge"])

def ser(db,d):
    chunks=db.scalar(select(func.count()).select_from(KnowledgeChunk).where(KnowledgeChunk.document_id==d.id)) or 0
    return {"id":d.id,"title":d.title,"type":d.file_type,"version":d.version,"status":d.status,"scope":d.scope,"quality":d.quality,"chunks":chunks,"updated_at":d.updated_at}

@router.get("")
def list_docs(user:User=Depends(require("knowledge:read")),db:Session=Depends(get_db)):
    docs=db.scalars(select(KnowledgeDocument).where(KnowledgeDocument.org_id==user.org_id).order_by(KnowledgeDocument.updated_at.desc())).all()
    return [ser(db,d) for d in docs]

@router.post("")
def create_doc(body:DocumentCreate,user:User=Depends(require("knowledge:write")),db:Session=Depends(get_db)):
    d=KnowledgeDocument(id=uid("KB"),org_id=user.org_id,title=body.title,file_type=body.file_type.upper(),version=body.version,status="Processando",scope=body.scope,source_text=body.source_text)
    db.add(d); enqueue(db,d); record(db,user=user,org_id=user.org_id,action="DOC_PUBLISHED",resource=f"Documento {d.id}",detail=f"{d.title} · {d.version}"); db.commit(); return ser(db,d)

@router.post("/{doc_id}/reprocess")
def reprocess(doc_id:str,user:User=Depends(require("knowledge:reprocess")),db:Session=Depends(get_db)):
    d=db.scalar(select(KnowledgeDocument).where(KnowledgeDocument.id==doc_id,KnowledgeDocument.org_id==user.org_id))
    if not d: raise HTTPException(404)
    enqueue(db,d); record(db,user=user,org_id=user.org_id,action="DOCUMENT_REPROCESS",resource=f"Documento {d.id}",detail=f"Versão {d.version} reenfileirada"); db.commit(); return {"id":d.id,"status":d.status}

@router.put("/{doc_id}")
def update_doc(doc_id:str,body:DocumentUpdate,user:User=Depends(require("knowledge:write")),db:Session=Depends(get_db)):
    d=db.scalar(select(KnowledgeDocument).where(KnowledgeDocument.id==doc_id,KnowledgeDocument.org_id==user.org_id))
    if not d: raise HTTPException(404)
    d.title=body.title; d.version=body.version; d.scope=body.scope; d.updated_at=datetime.now(timezone.utc)
    record(db,user=user,org_id=user.org_id,action="DOC_UPDATED",resource=f"Documento {d.id}",detail=f"{d.title} · {d.version} · {d.scope}")
    db.commit(); return ser(db,d)
