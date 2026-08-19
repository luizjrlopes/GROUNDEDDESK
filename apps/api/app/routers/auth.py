from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
from ..schemas import DemoLoginIn
from ..security import issue_token
router=APIRouter(prefix="/auth",tags=["auth"])

@router.get("/demo-users")
def demo_users(db:Session=Depends(get_db)):
    users=db.scalars(select(User).order_by(User.role,User.name)).all()
    return [{"id":u.id,"name":u.name,"role":u.role,"org_id":u.org_id} for u in users]

@router.post("/demo-login")
def demo_login(body:DemoLoginIn,db:Session=Depends(get_db)):
    user=db.get(User,body.user_id)
    if not user: raise HTTPException(404,"Demo user not found")
    return {"token":issue_token(user),"user":{"id":user.id,"name":user.name,"role":user.role,"org_id":user.org_id}}
