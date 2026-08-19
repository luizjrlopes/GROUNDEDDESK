from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import AuditEvent, KnowledgeDocument, Ticket, User
from ..security import current_user
router=APIRouter(prefix="/dashboard",tags=["dashboard"])
@router.get("")
def dashboard(user:User=Depends(current_user),db:Session=Depends(get_db)):
    tickets=db.scalar(select(func.count()).select_from(Ticket).where(Ticket.org_id==user.org_id,Ticket.status!="Fechado")) or 0
    docs=db.scalar(select(func.count()).select_from(KnowledgeDocument).where(KnowledgeDocument.org_id==user.org_id,KnowledgeDocument.status=="Indexado")) or 0
    audits=db.scalars(select(AuditEvent).where(AuditEvent.org_id==user.org_id).order_by(AuditEvent.created_at.desc()).limit(6)).all()
    return {"open_tickets":tickets,"sla_ok":92,"groundedness_avg":93,"indexed_documents":docs,"recent_audit":[{"action":a.action,"resource":a.resource,"detail":a.detail,"created_at":a.created_at} for a in audits]}
