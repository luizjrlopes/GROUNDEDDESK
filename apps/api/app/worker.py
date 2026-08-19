import time
from datetime import datetime, timezone
from sqlalchemy import select
from .config import settings
from .db import SessionLocal, init_db
from .ingestion import process_job
from .models import IngestionJob

def claim(db):
    stmt=select(IngestionJob).where(IngestionJob.status=="PENDING").order_by(IngestionJob.created_at).with_for_update(skip_locked=True).limit(1)
    job=db.scalar(stmt)
    if job:
        job.status="PROCESSING"; job.attempts+=1; job.updated_at=datetime.now(timezone.utc); db.commit()
    return job

def main():
    init_db()
    while True:
        with SessionLocal() as db:
            job=claim(db)
            if job:
                try:
                    process_job(db,job); db.commit()
                except Exception as exc:
                    db.rollback(); fresh=db.get(IngestionJob,job.id)
                    if fresh:
                        fresh.status="FAILED"; fresh.last_error=str(exc); fresh.updated_at=datetime.now(timezone.utc); db.commit()
        time.sleep(settings.worker_poll_seconds)
if __name__=="__main__": main()
