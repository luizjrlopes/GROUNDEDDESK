from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import ai, audit, auth, dashboard, demo, knowledge, search, tickets
app=FastAPI(title="GroundedDesk API",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_list,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
for router in [auth.router,dashboard.router,tickets.router,knowledge.router,search.router,ai.router,audit.router,demo.router]: app.include_router(router)
@app.get("/health")
def health(): return {"status":"ok"}
