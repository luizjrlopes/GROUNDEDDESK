from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from ..audit import record
from ..db import get_db
from ..domain import can, can_transition
from ..models import Ticket, TicketMessage, User, uid
from ..schemas import ReplyIn, TicketCreate, TransitionIn
from ..security import current_user
router=APIRouter(prefix="/tickets",tags=["tickets"])

def visible_stmt(user:User):
    stmt=select(Ticket).options(selectinload(Ticket.messages)).where(Ticket.org_id==user.org_id)
    if user.role=="requester": stmt=stmt.where(Ticket.requester_name==user.name)
    return stmt

def serialize(t:Ticket):
    return {"id":t.id,"subject":t.subject,"requester":t.requester_name,"queue":t.queue,"priority":t.priority,"status":t.status,"sla":t.sla_remaining,"assignee":t.assignee_name,"category":t.category,"sentiment":t.sentiment,"created_at":t.created_at,"messages":[{"id":m.id,"author":m.author_name,"kind":m.kind,"body":m.body,"created_at":m.created_at} for m in t.messages]}

@router.get("")
def list_tickets(user:User=Depends(current_user),db:Session=Depends(get_db)):
    if user.role!="requester" and not can(user.role,"tickets:read"): raise HTTPException(403)
    return [serialize(t) for t in db.scalars(visible_stmt(user).order_by(Ticket.created_at.desc())).unique().all()]

@router.get("/{ticket_id}")
def get_ticket(ticket_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
    if user.role!="requester" and not can(user.role,"tickets:read"): raise HTTPException(403)
    t=db.scalars(visible_stmt(user).where(Ticket.id==ticket_id)).unique().first()
    if not t: raise HTTPException(404,"Ticket not found")
    return serialize(t)

@router.post("")
def create_ticket(body:TicketCreate,user:User=Depends(current_user),db:Session=Depends(get_db)):
    if not can(user.role,"tickets:create"): raise HTTPException(403)
    requester=user.name if user.role=="requester" else (body.requester_name or user.name)
    t=Ticket(id=uid("GD"),org_id=user.org_id,subject=body.subject,requester_name=requester,queue=body.queue,priority=body.priority,status="Aberto")
    t.messages.append(TicketMessage(author_name=requester,kind="customer",body=body.description))
    db.add(t); record(db,user=user,org_id=user.org_id,action="TICKET_CREATED",resource=f"Ticket {t.id}",detail=body.subject); db.commit(); db.refresh(t)
    return serialize(t)

@router.post("/{ticket_id}/messages")
def add_message(ticket_id:str,body:ReplyIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
    t=db.scalars(visible_stmt(user).where(Ticket.id==ticket_id)).unique().first()
    if not t: raise HTTPException(404,"Ticket not found")
    if user.role=="requester" and not can(user.role,"tickets:comment"): raise HTTPException(403)
    if user.role!="requester" and not can(user.role,"tickets:reply"): raise HTTPException(403)
    kind="customer" if user.role=="requester" else "agent"
    t.messages.append(TicketMessage(author_name=user.name,kind=kind,body=body.body))
    action="TICKET_COMMENTED" if kind=="customer" else "TICKET_REPLIED"
    record(db,user=user,org_id=user.org_id,action=action,resource=f"Ticket {t.id}",detail=f"Mensagem adicionada por {user.name}")
    db.commit(); return serialize(t)

@router.post("/{ticket_id}/transition")
def transition(ticket_id:str,body:TransitionIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
    if not can(user.role,"tickets:transition"): raise HTTPException(403)
    t=db.scalar(select(Ticket).where(Ticket.id==ticket_id,Ticket.org_id==user.org_id))
    if not t: raise HTTPException(404)
    if not can_transition(t.status,body.status): raise HTTPException(409,f"Invalid transition {t.status} -> {body.status}")
    old=t.status; t.status=body.status
    record(db,user=user,org_id=user.org_id,action="TICKET_TRANSITIONED",resource=f"Ticket {t.id}",detail=f"{old} -> {body.status}")
    db.commit(); return {"id":t.id,"status":t.status}

@router.post("/{ticket_id}/pause-sla")
def pause_sla(ticket_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
    if not can(user.role,"tickets:transition"): raise HTTPException(403)
    t=db.scalar(select(Ticket).where(Ticket.id==ticket_id,Ticket.org_id==user.org_id))
    if not t: raise HTTPException(404)
    record(db,user=user,org_id=user.org_id,action="SLA_PAUSED",resource=f"Ticket {t.id}",detail="SLA pausado com justificativa demonstrativa")
    db.commit(); return {"ok":True}

@router.post("/{ticket_id}/escalate")
def escalate(ticket_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
    if not can(user.role,"tickets:transition"): raise HTTPException(403)
    t=db.scalar(select(Ticket).where(Ticket.id==ticket_id,Ticket.org_id==user.org_id))
    if not t: raise HTTPException(404)
    old=t.queue; t.queue="Network Operations"
    record(db,user=user,org_id=user.org_id,action="TICKET_ESCALATED",resource=f"Ticket {t.id}",detail=f"{old} -> {t.queue}")
    db.commit(); return {"id":t.id,"queue":t.queue}
