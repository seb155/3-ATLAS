from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class NoteBase(BaseModel):
    title: str
    content: Optional[str] = None
    parent_id: Optional[int] = None
    is_folder: bool = False


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    parent_id: Optional[int] = None


class Note(NoteBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NoteWithBacklinks(Note):
    backlinks: List[dict] = []
