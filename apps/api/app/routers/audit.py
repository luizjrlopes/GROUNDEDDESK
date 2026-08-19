from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import AuditEvent, User
from ..security import require
router=APIRouter(prefix="/audit",tags=["audit"])
@router.get("")
def list_audit(user:User=Depends(require("audit:read")),db:Session=Depends(get_db)):
    rows=db.scalars(select(AuditEvent).where(AuditEvent.org_id==user.org_id).order_by(AuditEvent.created_at.desc()).limit(200)).all()
    return [{"id":x.id,"at":x.created_at,"actor":x.actor_name,"role":x.actor_role,"action":x.action,"resource":x.resource,"detail":x.detail} for x in rows]
