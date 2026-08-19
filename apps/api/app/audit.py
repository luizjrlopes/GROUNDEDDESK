from sqlalchemy.orm import Session
from .models import AuditEvent, User

def record(db: Session, *, user: User | None, org_id: str, action: str, resource: str, detail: str, metadata: dict | None=None) -> None:
    db.add(AuditEvent(org_id=org_id, actor_id=user.id if user else None, actor_name=user.name if user else "GroundedDesk", actor_role=user.role if user else "system", action=action, resource=resource, detail=detail, metadata_json=metadata or {}))
