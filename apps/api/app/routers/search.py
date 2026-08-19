from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..audit import record
from ..db import get_db
from ..models import User
from ..rag import search
from ..schemas import SearchIn
from ..security import require
router=APIRouter(prefix="/search",tags=["search"])
@router.post("")
def run_search(body:SearchIn,user:User=Depends(require("search:read")),db:Session=Depends(get_db)):
    results=search(db,org_id=user.org_id,query=body.query,scope=body.scope,hybrid=body.hybrid)
    record(db,user=user,org_id=user.org_id,action="RETRIEVAL_COMPLETED",resource="Knowledge search",detail=f"query={body.query} · results={len(results)}",metadata={"hybrid":body.hybrid}); db.commit()
    return {"query":body.query,"hybrid":body.hybrid,"results":results}
