from __future__ import annotations
from pydantic import BaseModel, Field

class DemoLoginIn(BaseModel): user_id: str
class SessionOut(BaseModel): token: str; user: dict
class TicketCreate(BaseModel): subject: str; description: str; queue: str = "Workplace"; priority: str = "Média"; requester_name: str | None = None
class ReplyIn(BaseModel): body: str = Field(min_length=1)
class TransitionIn(BaseModel): status: str
class DocumentCreate(BaseModel): title: str; file_type: str = "MD"; version: str = "v1.0"; scope: str; source_text: str = ""
class DocumentUpdate(BaseModel): title: str; version: str; scope: str
class SearchIn(BaseModel): query: str = Field(min_length=2); scope: str | None = None; hybrid: bool = True
class FlagIn(BaseModel): value: bool
