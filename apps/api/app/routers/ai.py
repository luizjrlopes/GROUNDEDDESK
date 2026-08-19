from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..ai import provider
from ..audit import record
from ..db import get_db
from ..models import SystemFlag, Ticket, User
from ..rag import search
from ..schemas import FlagIn
from ..security import require
router=APIRouter(prefix="/ai",tags=["ai"])

def failure(db:Session,org_id:str)->bool:
    flag=db.scalar(select(SystemFlag).where(SystemFlag.org_id==org_id,SystemFlag.key=="ai_failure"))
    return bool(flag and flag.value)

@router.post("/ticket/{ticket_id}")
def draft(ticket_id:str,user:User=Depends(require("ai:use")),db:Session=Depends(get_db)):
    t=db.scalar(select(Ticket).where(Ticket.id==ticket_id,Ticket.org_id==user.org_id))
    if not t: raise HTTPException(404)
    if failure(db,user.org_id):
        record(db,user=user,org_id=user.org_id,action="AI_FALLBACK_USED",resource=f"Ticket {t.id}",detail="Provider indisponível; nenhuma resposta automática produzida"); db.commit()
        return {"mode":"fallback","answer":"Provider de IA indisponível. Continue o atendimento manualmente ou tente novamente.","groundedness":0,"citations":[]}
    results=search(db,org_id=user.org_id,query=f"{t.subject} {t.category}",scope=t.queue if t.queue in {"Workplace","Aplicações","IAM","Infra"} else None,hybrid=True,limit=4)
    answer=provider().answer(t.subject,[r["content"] for r in results])
    citations=[{"document_id":r["document_id"],"title":r["title"],"version":r["version"],"section":r["section"],"score":r["rerank"]} for r in results]
    record(db,user=user,org_id=user.org_id,action="AI_DRAFT_GENERATED",resource=f"Ticket {t.id}",detail=f"{len(citations)} citações · groundedness {answer.groundedness}%"); db.commit()
    return {"mode":"grounded","answer":answer.text,"groundedness":answer.groundedness,"citations":citations}

@router.post("/failure-mode")
def failure_mode(body:FlagIn,user:User=Depends(require("ai:use")),db:Session=Depends(get_db)):
    flag=db.scalar(select(SystemFlag).where(SystemFlag.org_id==user.org_id,SystemFlag.key=="ai_failure"))
    if not flag: flag=SystemFlag(org_id=user.org_id,key="ai_failure",value=body.value); db.add(flag)
    else: flag.value=body.value
    record(db,user=user,org_id=user.org_id,action="AI_FAILURE_MODE_CHANGED",resource="AI provider",detail=f"enabled={body.value}"); db.commit(); return {"enabled":body.value}
