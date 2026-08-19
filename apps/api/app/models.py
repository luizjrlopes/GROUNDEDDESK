from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from .config import settings
from .db import Base

def now(): return datetime.now(timezone.utc)
def uid(prefix: str): return f"{prefix}-{uuid4().hex[:8].upper()}"

class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(40), index=True)
    org: Mapped[Organization] = relationship()

class Ticket(Base):
    __tablename__ = "tickets"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    subject: Mapped[str] = mapped_column(String(240))
    requester_name: Mapped[str] = mapped_column(String(120), index=True)
    queue: Mapped[str] = mapped_column(String(80))
    priority: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(40), index=True)
    sla_remaining: Mapped[int] = mapped_column(Integer, default=100)
    assignee_name: Mapped[str] = mapped_column(String(120), default="Não atribuído")
    category: Mapped[str] = mapped_column(String(80), default="Não classificado")
    sentiment: Mapped[str] = mapped_column(String(40), default="Neutro")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    messages: Mapped[list[TicketMessage]] = relationship(back_populates="ticket", cascade="all, delete-orphan", order_by="TicketMessage.created_at")
    attachments: Mapped[list[TicketAttachment]] = relationship(back_populates="ticket", cascade="all, delete-orphan")

class TicketAttachment(Base):
    __tablename__ = "ticket_attachments"
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: uid("ATT"))
    ticket_id: Mapped[str] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(String(240))
    media_type: Mapped[str] = mapped_column(String(120), default="application/octet-stream")
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    ticket: Mapped[Ticket] = relationship(back_populates="attachments")

class TicketMessage(Base):
    __tablename__ = "ticket_messages"
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: uid("MSG"))
    ticket_id: Mapped[str] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"), index=True)
    author_name: Mapped[str] = mapped_column(String(120))
    kind: Mapped[str] = mapped_column(String(30))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    ticket: Mapped[Ticket] = relationship(back_populates="messages")

class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    title: Mapped[str] = mapped_column(String(240))
    file_type: Mapped[str] = mapped_column(String(20))
    version: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(40), index=True)
    scope: Mapped[str] = mapped_column(String(80), index=True)
    quality: Mapped[int] = mapped_column(Integer, default=0)
    source_text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: uid("CH"))
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("knowledge_documents.id", ondelete="CASCADE"), index=True)
    section: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(settings.local_embedding_dimensions))

class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: uid("JOB"))
    org_id: Mapped[str] = mapped_column(String(40), index=True)
    document_id: Mapped[str] = mapped_column(String(40), index=True)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: uid("AUD"))
    org_id: Mapped[str] = mapped_column(String(40), index=True)
    actor_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    actor_name: Mapped[str] = mapped_column(String(120))
    actor_role: Mapped[str] = mapped_column(String(60))
    action: Mapped[str] = mapped_column(String(100), index=True)
    resource: Mapped[str] = mapped_column(String(180))
    detail: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)

class SystemFlag(Base):
    __tablename__ = "system_flags"
    __table_args__ = (UniqueConstraint("org_id", "key", name="uq_system_flag"),)
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: uid("FLAG"))
    org_id: Mapped[str] = mapped_column(String(40), index=True)
    key: Mapped[str] = mapped_column(String(80))
    value: Mapped[bool] = mapped_column(Boolean, default=False)
