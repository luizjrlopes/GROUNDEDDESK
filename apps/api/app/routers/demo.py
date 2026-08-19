from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
from ..security import current_user
from ..seed import reset_demo
router=APIRouter(prefix="/demo",tags=["demo"])
@router.post("/reset")
def reset(user:User=Depends(current_user),db:Session=Depends(get_db)):
    if user.role not in {"manager","kbadmin"}: raise HTTPException(403,"Manager or Admin KB required")
    reset_demo(db); return {"ok":True}
